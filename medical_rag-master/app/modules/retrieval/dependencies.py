from __future__ import annotations

from app.core.config import get_settings
from app.db.vector.qdrant import QdrantProvider
from app.modules.retrieval.service import RetrievalService
from app.shared.embedder import Embedder

settings = get_settings()


def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedder=Embedder(
            api_key=settings.embedding_api_key, model=settings.embedding_model
        ),
        vector_db=QdrantProvider(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection,
            dims=settings.embedding_dimension,
        ),
    )
