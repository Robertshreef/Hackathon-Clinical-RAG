from fastembed import SparseTextEmbedding
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client.http import models as qmodels


class Embedder:
    def __init__(
        self,
        api_key: str,
        model: str,
        sparse_model: str = "Qdrant/bm25",
    ):
        self._dense = GoogleGenerativeAIEmbeddings(
            model=model,
            api_key=api_key,  # type: ignore
        )

        self._sparse = SparseTextEmbedding(
            model_name=sparse_model,
        )

    async def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return await self._dense.aembed_query(text)

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return await self._dense.aembed_documents(texts)

    def embed_sparse(
        self,
        texts: list[str],
    ) -> list[qmodels.SparseVector]:
        embeddings = list(self._sparse.embed(texts))

        return [
            qmodels.SparseVector(
                indices=embedding.indices.tolist(),
                values=embedding.values.tolist(),
            )
            for embedding in embeddings
        ]

    def embed_sparse_query(
        self,
        text: str,
    ) -> qmodels.SparseVector:
        return self.embed_sparse([text])[0]
