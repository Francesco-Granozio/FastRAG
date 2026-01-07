import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import inngest
import os
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


def save_uploaded_pdf(file: UploadFile, uploads_dir: Path) -> Path:
    """Save uploaded PDF file to disk."""
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.filename
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> str:
    """Send Inngest event for PDF ingestion and return event ID."""
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )
    return result[0] if result else None


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and trigger ingestion."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    uploads_dir = Path("uploads")
    try:
        pdf_path = save_uploaded_pdf(file, uploads_dir)
        event_id = await send_rag_ingest_event(pdf_path)

        return JSONResponse(
            content={
                "message": "File uploaded successfully",
                "filename": file.filename,
                "event_id": event_id,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/upload/status/{event_id}")
async def get_upload_status(event_id: str):
    """Get the status of an upload event."""
    import requests

    inngest_api_base = os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")
    url = f"{inngest_api_base}/events/{event_id}/runs"

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        runs = data.get("data", [])

        if runs:
            run = runs[0]
            status = run.get("status", "Unknown")
            return {
                "event_id": event_id,
                "status": status,
                "run": run,
            }
        else:
            return {
                "event_id": event_id,
                "status": "Pending",
                "run": None,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching status: {str(e)}")
