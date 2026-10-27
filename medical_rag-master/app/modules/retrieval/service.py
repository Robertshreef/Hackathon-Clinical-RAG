from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.vector.qdrant import QdrantProvider
    from app.shared.embedder import Embedder
    from app.shared.schemas import ChunkMeta


class RetrievalService:
    def __init__(
        self,
        embedder: Embedder,
        vector_db: QdrantProvider,
    ):
        self._embedder = embedder
        self._vector_db = vector_db

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: float = 0.0,
    ) -> list[ChunkMeta]:

        dense_vector = await self._embedder.embed_query(query)

        sparse_vector = self._embedder.embed_sparse_query(query)

        return await self._vector_db.hybrid_search(
            dense_query=dense_vector,
            sparse_query=sparse_vector,
            top_k=top_k,
            score_threshold=score_threshold,
        )
