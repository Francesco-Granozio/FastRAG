import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
import asyncio
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from llm_providers import get_llm_provider
from config import ModelConfig
from custom_types import (
    RAQQueryResult,
    RAGSearchResult,
    RAGUpsertResult,
    RAGChunkAndSrc,
)

load_dotenv()
ModelConfig.validate()

# ============================================================================
# CONSTANTS - LLM generation settings
# ============================================================================
DEFAULT_MAX_TOKENS = 1024  # Numero massimo di token da generare per risposta LLM
DEFAULT_TEMPERATURE = 0.2  # Temperatura per generazione LLM (0.0-1.0, più bassa = più deterministica)
DEFAULT_TOP_K = 5  # Numero di chunk da recuperare per default nelle query

# ============================================================================
# CONSTANTS - Rate limiting settings
# ============================================================================
THROTTLE_LIMIT = 2  # Numero massimo di esecuzioni per periodo di throttle
THROTTLE_PERIOD_MINUTES = 1  # Periodo per throttle (minuti)
RATE_LIMIT_LIMIT = 1  # Numero massimo di esecuzioni per periodo di rate limit
RATE_LIMIT_PERIOD_HOURS = 4  # Periodo per rate limit (ore)

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(limit=THROTTLE_LIMIT, period=datetime.timedelta(minutes=THROTTLE_PERIOD_MINUTES)),
    rate_limit=inngest.RateLimit(
        limit=RATE_LIMIT_LIMIT,
        period=datetime.timedelta(hours=RATE_LIMIT_PERIOD_HOURS),
        key="event.data.source_id",
    ),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}"))
            for i in range(len(chunks))
        ]
        payloads = [
            {"source": source_id, "text": chunks[i]} for i in range(len(chunks))
        ]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run(
        "load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc
    )
    ingested = await ctx.step.run(
        "embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult
    )
    return ingested.model_dump()


@inngest_client.create_function(
    fn_id="RAG: Query PDF", trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question: str, top_k: int = DEFAULT_TOP_K) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", DEFAULT_TOP_K))

    found = await ctx.step.run(
        "embed-and-search",
        lambda: _search(question, top_k),
        output_type=RAGSearchResult,
    )

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )

    llm_provider = get_llm_provider()
    adapter = llm_provider.get_inngest_adapter()

    if adapter is not None:
        # Use inngest adapter (e.g., OpenAI)
        res = await ctx.step.ai.infer(
            "llm-answer",
            adapter=adapter,
            body={
                "max_tokens": DEFAULT_MAX_TOKENS,
                "temperature": DEFAULT_TEMPERATURE,
                "messages": [
                    {
                        "role": "system",
                        "content": "You answer questions using only the provided context.",
                    },
                    {"role": "user", "content": user_content},
                ],
            },
        )
        answer = res["choices"][0]["message"]["content"].strip()
    else:
        # Use direct provider call (e.g., Ollama, Google, Anthropic)
        # For non-inngest providers, call directly (still tracked by inngest function)
        answer = await llm_provider.generate(
            messages=[
                {
                    "role": "system",
                    "content": "You answer questions using only the provided context.",
                },
                {"role": "user", "content": user_content},
            ],
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
        )
    return {
        "answer": answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts),
    }


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])
