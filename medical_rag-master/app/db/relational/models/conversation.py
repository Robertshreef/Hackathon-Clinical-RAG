from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.db.relational.models.base import GUID, Base
from pydantic import BaseModel
from sqlalchemy import ForeignKey, String, UniqueConstraint, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.db.relational.models.message import Message
    from app.db.relational.models.user import User


class PydanticJSON(types.TypeDecorator):
    """Converts Pydantic objects to JSON dicts for the DB and back."""

    impl = types.JSON
    cache_ok = True

    def __init__(self, pydantic_model: type[BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pydantic_model = pydantic_model

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.pydantic_model):
            return value.model_dump(mode="json")
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.pydantic_model.model_validate(value)


class Conversation(Base):
    __tablename__ = "conversation"

    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.created_at",
        cascade="all, delete-orphan",
    )
    user: Mapped[User] = relationship("User", back_populates="conversations")

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_conversation_name_user_id"),
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id!r}>"
