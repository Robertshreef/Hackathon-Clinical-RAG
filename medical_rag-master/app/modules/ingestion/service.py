from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from app.modules.ingestion.parser import PdfParser

if TYPE_CHECKING:
    from uuid import UUID

    from app.db.vector.qdrant import QdrantProvider
    from app.shared.embedder import Embedder
    from app.shared.vlm import VLM


class IngestionService:
    def __init__(
        self,
        data_dir: Path,
        embedder: Embedder,
        vlm: VLM,
        vector_db: QdrantProvider,
    ):
        self.data_dir = data_dir
        self.embedder = embedder
        self.vlm = vlm
        self.vector_db = vector_db

    async def ingest(self):
        parser = PdfParser(vlm=self.vlm)

        pdf_files = list(self.data_dir.rglob("*.pdf"))

        for file_path in pdf_files:
            chunks_meta = parser.load(file_path=file_path)

            chunks_ids: list[UUID] = [uuid4() for _ in chunks_meta]
            chunks_content: list[str] = [c.content for c in chunks_meta]

            dense_vectors = []
            sparse_vectors = []

            for i in range(0, len(chunks_content), 50):
                chunks_partial = chunks_content[i : i + 50]

                dense_vectors_partial = await self.embedder.embed(chunks_partial)
                dense_vectors.extend(dense_vectors_partial)

                sparse_vectors_partial = self.embedder.embed_sparse(chunks_partial)
                sparse_vectors.extend(sparse_vectors_partial)

                await asyncio.sleep(5)

            await self.vector_db.upsert(
                ids=chunks_ids,
                dense_vectors=dense_vectors,
                sparse_vectors=sparse_vectors,
                metadatas=chunks_meta,
            )
