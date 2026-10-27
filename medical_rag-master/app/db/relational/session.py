from collections.abc import AsyncGenerator

from app.core.config import get_settings
from app.db.relational.exceptions import (
    DatabaseError,
    DBIntegrityError,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ───────────────────────────────── Async Session for fastapi ──────────────────────────────────
settings = get_settings()

_is_sqlite = settings.async_url.startswith("sqlite")

if _is_sqlite:
    async_engine = create_async_engine(
        settings.async_url,
        echo=settings.echo,
        # SQLite doesn't support pool_size / max_overflow
        connect_args={"check_same_thread": False},
    )
else:
    async_engine = create_async_engine(
        settings.async_url,
        echo=settings.echo,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def create_all_tables() -> None:
    """Create all tables in the database (idempotent)."""
    from app.db.relational.models import Base  # noqa: F811

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides transactional async DB sessions."""
    async with async_session_factory() as session:
        try:
            yield session
        except IntegrityError as exc:
            await session.rollback()
            raise DBIntegrityError(str(exc.orig)) from exc
        except SQLAlchemyError as exc:
            await session.rollback()
            raise DatabaseError(str(exc)) from exc
        except Exception:
            await session.rollback()
            raise
