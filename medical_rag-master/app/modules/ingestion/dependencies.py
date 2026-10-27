from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.db.vector.qdrant import QdrantProvider
from app.modules.ingestion.service import IngestionService
from app.shared.embedder import Embedder
from app.shared.vlm import VLM

settings = get_settings()


async def get_ingestion_service() -> IngestionService:
    return IngestionService(
        data_dir=Path(settings.src_dir),
        embedder=Embedder(
            api_key=settings.embedding_api_key, model=settings.embedding_model
        ),
        vlm=VLM(model=settings.vlm_model, api_key=settings.vlm_api_key),
        vector_db=QdrantProvider(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection,
            dims=settings.embedding_dimension,
        ),
    )
