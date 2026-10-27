from __future__ import annotations

from uuid import UUID

from app.shared.schemas import ChunkMeta
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.models import (
    Distance,
    # FieldCondition,
    # Filter,
    # MatchAny,
    # MatchValue,
    VectorParams,
)


# Singleton in-memory client — shared across ALL QdrantProvider instances so
# data written during ingestion is visible to retrieval (and vice-versa).
_IN_MEMORY_CLIENT: AsyncQdrantClient | None = None


def _get_in_memory_client() -> AsyncQdrantClient:
    global _IN_MEMORY_CLIENT
    if _IN_MEMORY_CLIENT is None:
        _IN_MEMORY_CLIENT = AsyncQdrantClient(location=":memory:")
    return _IN_MEMORY_CLIENT


class QdrantProvider:
    def __init__(self, url: str, collection_name: str, dims: int) -> None:
        self._collection = collection_name
        self._dims = dims
        if url == ":memory:":
            self._client = _get_in_memory_client()
        else:
            self._client = AsyncQdrantClient(url=str(url))

    async def ensure_collection(self) -> bool:
        exists = await self._client.collection_exists(self._collection)

        if not exists:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config={
                    "dense": VectorParams(
                        size=self._dims,
                        distance=Distance.COSINE,
                    ),
                },
                sparse_vectors_config={
                    "sparse": qmodels.SparseVectorParams(
                        modifier=qmodels.Modifier.IDF,
                    ),
                },
            )
            return False

        return True

    async def upsert(
        self,
        ids: list[UUID],
        dense_vectors: list[list[float]],
        sparse_vectors: list[qmodels.SparseVector],
        metadatas: list[ChunkMeta],
    ) -> None:

        if not (
            len(ids) == len(dense_vectors) == len(sparse_vectors) == len(metadatas)
        ):
            raise ValueError("All inputs must have the same length")

        points = [
            qmodels.PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vector,
                    "sparse": sparse_vector,
                },
                payload=metadata.model_dump(),
            )
            for point_id, dense_vector, sparse_vector, metadata in zip(
                ids,
                dense_vectors,
                sparse_vectors,
                metadatas,
            )
        ]

        await self._client.upsert(
            collection_name=self._collection,
            points=points,
            wait=True,
        )

    async def hybrid_search(
        self,
        dense_query: list[float],
        sparse_query: qmodels.SparseVector,
        top_k: int,
        score_threshold: float = 0.0,
    ) -> list[ChunkMeta]:

        results = await self._client.query_points(
            collection_name=self._collection,
            prefetch=[
                qmodels.Prefetch(
                    query=dense_query,
                    using="dense",
                    limit=top_k * 2,
                ),
                qmodels.Prefetch(
                    query=sparse_query,
                    using="sparse",
                    limit=top_k * 2,
                ),
            ],
            query=qmodels.FusionQuery(
                fusion=qmodels.Fusion.RRF,
            ),
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )

        search_results: list[ChunkMeta] = []

        for point in results.points:
            if point.payload is None:
                continue

            search_results.append(ChunkMeta.model_validate(point.payload))

        return search_results

    # async def scroll(
    #     self,
    #     user_id: UUID,
    #     course_id: UUID,
    #     limit: int = 10,
    #     with_payload: bool = True,
    #     with_vectors: bool = False,
    # ) -> list[SearchResult]:
    #     """
    #     Scrolls through the collection with hard user + course filters
    #     and returns a chunk of records.
    #     """
    #     candidate_pool_size = max(100, limit * 3)

    #     # Define Qdrant filter for metadata
    #     # Adjust "user_id" or "metadata.user_id" depending on how your payload is structured
    #     qdrant_filter = Filter(
    #         must=[
    #             FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
    #             FieldCondition(key="course_id", match=MatchValue(value=str(course_id))),
    #         ]
    #     )

    #     records, _ = self._client.scroll(
    #         collection_name=self._collection,
    #         scroll_filter=qdrant_filter,  # Inject the filter here
    #         limit=candidate_pool_size,
    #         with_payload=with_payload,
    #         with_vectors=with_vectors,
    #     )

    #     if not records:
    #         return []

    #     random.shuffle(records)
    #     records = records[:limit]

    #     return [
    #         SearchResult(
    #             content=record.payload.get("content"),  # type: ignore
    #             score=1.0,
    #             document_id=record.payload.get("document_id"),  # type: ignore
    #             index=record.payload.get("index"),  # type: ignore
    #             chunk_id=str(record.id),
    #             starting_page=record.payload.get("starting_page"),  # type: ignore
    #             end_page=record.payload.get("end_page"),  # type: ignore
    #         )
    #         for record in records
    #     ]
