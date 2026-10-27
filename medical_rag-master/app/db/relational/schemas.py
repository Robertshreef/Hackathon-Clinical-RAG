from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.db.relational.constants import MessageRole
from pydantic import BaseModel


class TokenCreate(BaseModel):
    user_id: UUID
    token_hash: str
    expires_at: datetime
    revoked: bool = False


class TokenUpdate(BaseModel):
    expires_at: datetime | None = None
    revoked: bool | None = None


# ───────────────────────── User ─────────────────────────
class UserCreate(BaseModel):
    email: str
    full_name: str
    hashed_password: str


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    hashed_password: str | None = None


# ───────────────────────── Conversation ─────────────────────────
class ConversationCreate(BaseModel):
    name: str


class ConversationUpdate(BaseModel):
    name: str


# ───────────────────────── Message ─────────────────────────
class MessageCreate(BaseModel):
    role: MessageRole
    content: str
    token_count: int | None = None
