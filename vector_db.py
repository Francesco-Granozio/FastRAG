from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    NearestQuery,
    Filter,
    FieldCondition,
    MatchValue,
)
from data_loader import get_embedding_dimension
from collections import Counter

# ============================================================================
# CONSTANTS - Qdrant connection settings
# ============================================================================
DEFAULT_QDRANT_URL = "http://localhost:6333"  # URL del server Qdrant
DEFAULT_COLLECTION_NAME = "docs"  # Nome della collezione Qdrant di default
DEFAULT_QDRANT_TIMEOUT = 30  # Timeout per connessioni Qdrant (secondi)

# ============================================================================
# CONSTANTS - Query settings
# ============================================================================
SCROLL_BATCH_LIMIT = 1000  # Numero massimo di punti da recuperare per batch nello scroll
DEFAULT_CHUNKS_BY_SOURCE_LIMIT = 100  # Numero massimo di chunk da recuperare per source di default


class QdrantStorage:
    def __init__(self, url=DEFAULT_QDRANT_URL, collection=DEFAULT_COLLECTION_NAME, dim=None):
        self.client = QdrantClient(url=url, timeout=DEFAULT_QDRANT_TIMEOUT)
        self.collection = collection
        # Use provided dim or get from current embedding provider
        self.dim = dim if dim is not None else get_embedding_dimension()
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
            for i in range(len(ids))
        ]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5):
        # query_points accetta 'query' che può essere un vettore direttamente o un NearestQuery
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,  # Passa il vettore direttamente come query
            with_payload=True,
            limit=top_k,
        )
        contexts = []
        sources = set()

        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text:
                contexts.append(text)
                sources.add(source)

        return {"contexts": contexts, "sources": list(sources)}

    def get_all_sources(self) -> dict:
        """Recupera tutti i source_id unici con conteggio chunk."""
        sources_count = Counter()

        # Usa scroll per recuperare tutti i punti con payload
        # Scroll in batch per gestire grandi collezioni
        offset = None
        limit = SCROLL_BATCH_LIMIT

        while True:
            result, next_offset = self.client.scroll(
                collection_name=self.collection,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,  # Non serve il vettore per il conteggio
            )

            # Conta i chunk per ogni source
            for point in result:
                payload = getattr(point, "payload", None) or {}
                source = payload.get("source", "")
                if source:
                    sources_count[source] += 1

            # Se non c'è un next_offset, abbiamo finito
            if next_offset is None:
                break

            offset = next_offset

        # Converti Counter in dict e ordina per numero di chunk (decrescente)
        sources_dict = dict(sources_count)
        return {
            "sources": sources_dict,
            "total_sources": len(sources_dict),
            "total_chunks": sum(sources_dict.values()),
        }

    def get_chunks_by_source(self, source_id: str, limit: int = DEFAULT_CHUNKS_BY_SOURCE_LIMIT) -> list:
        """Recupera tutti i chunk per un source specifico."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Crea un filtro per il source_id
        filter_condition = Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=source_id))]
        )

        # Scroll con filtro
        chunks = []
        offset = None
        batch_limit = min(limit, SCROLL_BATCH_LIMIT)

        while len(chunks) < limit:
            result, next_offset = self.client.scroll(
                collection_name=self.collection,
                limit=batch_limit,
                offset=offset,
                scroll_filter=filter_condition,
                with_payload=True,
                with_vectors=False,
            )

            for point in result:
                payload = getattr(point, "payload", None) or {}
                chunk_data = {
                    "id": str(point.id),
                    "text": payload.get("text", ""),
                    "source": payload.get("source", ""),
                }
                chunks.append(chunk_data)

                if len(chunks) >= limit:
                    break

            if next_offset is None or len(chunks) >= limit:
                break

            offset = next_offset

        return chunks
