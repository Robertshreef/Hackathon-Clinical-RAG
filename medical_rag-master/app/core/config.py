from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "Medical RAG"
    upload_dir: str = "./data/uploads"
    src_dir: str = "./data/src"

    # --- Auth ---
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # --- Relational DB ---
    sync_url: str = ""
    async_url: str = ""
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    # --- Embedding ---
    embedding_provider: str = "google"
    embedding_model: str = "models/text-embedding-004"
    embedding_dimension: int = 768
    embedding_api_key: str = ""
    embedding_base_url: str | None = None

    # --- VLM ---
    vlm_model: str = "gemini-2.0-flash"
    vlm_api_key: str = ""
    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "medical_documents"

    # --- Chunking ---
    max_chunk_size: int = 1000

    # --- Retrieval ---
    retrieval_top_k: int = 5
    rrf_k: int = 60  # reciprocal rank fusion constant

    # --- LLM ---
    llm_provider: str = "google"
    llm_model: str = "gemini-2.0-flash"
    llm_api_key: str = ""

    # --- Chat ---
    context_window_limit: int = 4096


@lru_cache
def get_settings() -> Settings:
    return Settings()
