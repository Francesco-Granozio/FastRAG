import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import inngest
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Inngest client (singleton)
_inngest_client = None

def get_inngest_client() -> inngest.Inngest:
    global _inngest_client
    if _inngest_client is None:
        _inngest_client = inngest.Inngest(
            app_id="rag_app",
            is_production=False,
            serializer=inngest.PydanticSerializer(),
        )
    return _inngest_client

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

def fetch_runs(event_id: str) -> list[dict]:
    """Fetch runs for an event from Inngest API."""
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    event_id: str
    status: str
    message: str

@router.post("/query", response_model=QueryResponse)
async def query_pdf(request: QueryRequest):
    """Send a query to the LLM and return event ID for polling."""
    client = get_inngest_client()
    
    try:
        result = await client.send(
            inngest.Event(
                name="rag/query_pdf_ai",
                data={
                    "question": request.question,
                    "top_k": request.top_k,
                },
            )
        )
        event_id = result[0] if result else None
        
        if not event_id:
            raise HTTPException(status_code=500, detail="Failed to create query event")
        
        return QueryResponse(
            event_id=event_id,
            status="pending",
            message="Query submitted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting query: {str(e)}")

@router.get("/query/status/{event_id}")
async def get_query_status(event_id: str):
    """Get the status and result of a query."""
    try:
        runs = fetch_runs(event_id)
        
        if not runs:
            return {
                "event_id": event_id,
                "status": "pending",
                "result": None,
            }
        
        run = runs[0]
        status = run.get("status", "Unknown")
        output = run.get("output")
        
        if status in ("Completed", "Succeeded", "Success", "Finished"):
            return {
                "event_id": event_id,
                "status": "completed",
                "result": output or {},
            }
        elif status in ("Failed", "Cancelled"):
            error = run.get("error", "Unknown error")
            return {
                "event_id": event_id,
                "status": "failed",
                "error": error,
                "result": None,
            }
        else:
            return {
                "event_id": event_id,
                "status": "running",
                "result": None,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching query status: {str(e)}")

