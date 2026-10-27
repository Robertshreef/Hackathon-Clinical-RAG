from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.relational.models.user import User
from app.db.relational.repositories.token_repository import TokenRepository
from app.db.relational.repositories.user_repository import UserRepository
from app.db.relational.session import get_db
from app.modules.auth.service import AuthService

if TYPE_CHECKING:
    pass

# ── No-Auth bypass: always return (or create) a default local user ────────────

_BYPASS_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_BYPASS_EMAIL = "local@clinicalrag.local"


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:  # type: ignore[override]
    """
    AUTH BYPASS — no token required.
    Returns the first user in the DB, or auto-creates a default local user
    so the app works immediately without login.
    """
    # Try to find the pinned bypass user first
    user = await db.scalar(select(User).where(User.email == _BYPASS_EMAIL))
    if user is not None:
        return user

    # Fall back to any existing user
    any_user = await db.scalar(select(User).limit(1))
    if any_user is not None:
        return any_user

    # No users at all — create a default one on the fly
    default_user = User(
        id=_BYPASS_USER_ID,
        email=_BYPASS_EMAIL,
        hashed_password="bypass_no_password",
        full_name="Local User",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db.add(default_user)
    await db.commit()
    await db.refresh(default_user)
    return default_user


async def get_current_active_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias kept for compatibility — bypass always returns an active verified user."""
    return current_user


def require_role(*roles: str):
    """Auth bypass — role check is skipped, all roles permitted."""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        return current_user

    return checker


# Convenience aliases
AdminUser = Depends(require_role("admin"))


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        user_repository=UserRepository(db),
        token_repository=TokenRepository(db),
        settings=get_settings(),
    )
