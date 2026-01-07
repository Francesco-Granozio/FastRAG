from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from src.core.vector_db import QdrantStorage
import logging

# Usa il logger di uvicorn per logging consistente
logger = logging.getLogger("uvicorn")

router = APIRouter()

class FileInfo(BaseModel):
    source_id: str
    chunk_count: int

class FilesResponse(BaseModel):
    files: List[FileInfo]
    total_files: int
    total_chunks: int

class ChunkInfo(BaseModel):
    id: str
    text: str
    source: str

class ChunksResponse(BaseModel):
    chunks: List[ChunkInfo]
    total: int

class DeleteFilesRequest(BaseModel):
    source_ids: List[str]

@router.get("/files", response_model=FilesResponse)
async def get_all_files():
    """Get all embedded files with their chunk counts."""
    try:
        storage = QdrantStorage()
        sources_data = storage.get_all_sources()
        
        files = [
            FileInfo(source_id=source_id, chunk_count=count)
            for source_id, count in sources_data["sources"].items()
        ]
        
        return FilesResponse(
            files=files,
            total_files=sources_data["total_sources"],
            total_chunks=sources_data["total_chunks"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")

@router.get("/files/{source_id}/chunks", response_model=ChunksResponse)
async def get_file_chunks(source_id: str, limit: int = 20, offset: int = 0):
    """Get chunks for a specific file."""
    try:
        storage = QdrantStorage()
        chunks = storage.get_chunks_by_source(source_id, limit=limit + offset)
        
        # Apply offset
        chunks = chunks[offset:offset + limit]
        
        chunk_infos = [
            ChunkInfo(id=chunk["id"], text=chunk["text"], source=chunk["source"])
            for chunk in chunks
        ]
        
        # Get total count
        sources_data = storage.get_all_sources()
        total = sources_data["sources"].get(source_id, 0)
        
        return ChunksResponse(
            chunks=chunk_infos,
            total=total,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chunks: {str(e)}")

@router.delete("/files/{source_id}")
async def delete_file(source_id: str):
    """Delete a single file and all its chunks."""
    try:
        storage = QdrantStorage()
        deleted_count = storage.delete_by_source(source_id)
        
        return {
            "message": "File deleted successfully",
            "source_id": source_id,
            "chunks_deleted": deleted_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.delete("/files")
async def delete_files(request: DeleteFilesRequest):
    """Delete multiple files."""
    logger.info(f"[API DELETE] Received request to delete {len(request.source_ids)} files: {request.source_ids}")
    
    results = []
    errors = []
    
    for source_id in request.source_ids:
        logger.info(f"[API DELETE] Processing deletion for source_id: {source_id}")
        try:
            storage = QdrantStorage()
            deleted_count = storage.delete_by_source(source_id)
            logger.info(f"[API DELETE] Successfully deleted {deleted_count} chunks for source_id: {source_id}")
            
            results.append({
                "source_id": source_id,
                "chunks_deleted": deleted_count,
                "status": "success",
            })
        except Exception as e:
            logger.error(f"[API DELETE] Error deleting source_id {source_id}: {str(e)}", exc_info=True)
            errors.append({
                "source_id": source_id,
                "error": str(e),
                "status": "error",
            })
    
    logger.info(f"[API DELETE] Deletion summary: {len(results)} successful, {len(errors)} errors")
    
    # Se ci sono errori, restituisci 207 Multi-Status o 500 se tutti falliscono
    if errors:
        logger.warning(f"[API DELETE] Some deletions failed: {errors}")
        if len(errors) == len(request.source_ids):
            # Tutti i file hanno fallito
            logger.error(f"[API DELETE] All files failed to delete")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "All files failed to delete",
                    "errors": errors,
                }
            )
        else:
            # Alcuni file hanno fallito - restituisci 200 con informazioni sugli errori
            response = {
                "deleted": results,
                "errors": errors,
                "total_deleted": len(results),
                "total_errors": len(errors),
                "message": f"Some files failed to delete: {len(errors)} error(s)",
            }
            logger.info(f"[API DELETE] Returning partial success response: {response}")
            return response
    
    # Tutti i file cancellati con successo
    response = {
        "deleted": results,
        "errors": [],
        "total_deleted": len(results),
        "total_errors": 0,
        "message": "All files deleted successfully",
    }
    logger.info(f"[API DELETE] All deletions successful. Returning: {response}")
    return response

