from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from app.db.relational.models.refresh_token import RefreshToken
from sqlalchemy import select

if TYPE_CHECKING:
    from app.db.relational.schemas import TokenCreate, TokenUpdate
    from sqlalchemy.ext.asyncio import AsyncSession


class TokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, data: TokenCreate) -> RefreshToken:
        token = RefreshToken(**data.model_dump())
        self._session.add(token)
        await self._session.commit()
        await self._session.refresh(token)
        return token

    async def get_by_hash(self, hash: str) -> RefreshToken | None:
        return await self._session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash)
        )

    async def update(self, data: TokenUpdate, token: RefreshToken) -> RefreshToken:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(token, field, value)
        await self._session.commit()
        await self._session.refresh(token)
        return token

    async def get_all_by_user(self, user_id: UUID) -> Sequence[RefreshToken]:
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
        )
        return result.scalars().all()
