from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.vector.qdrant import QdrantProvider
from app.modules.auth.router import auth_router
from app.modules.chat.router import chat_router
from app.modules.ingestion.dependencies import get_ingestion_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create relational tables (idempotent — safe for dev & SQLite)
    from app.db.relational.session import create_all_tables
    await create_all_tables()

    existing = await QdrantProvider(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
        dims=settings.embedding_dimension,
    ).ensure_collection()
    if not existing:
        ingestion_service = await get_ingestion_service()
        await ingestion_service.ingest()  # Run ingestion on startup

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
