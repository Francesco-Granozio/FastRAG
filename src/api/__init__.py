from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

# Import all routers
from . import upload, query, files

api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(query.router, tags=["query"])
api_router.include_router(files.router, tags=["files"])

