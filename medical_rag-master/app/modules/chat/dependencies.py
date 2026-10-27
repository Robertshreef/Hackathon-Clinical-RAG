from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.config import get_settings
from app.db.relational.repositories.conversation_repository import (
    ConversationRepository,
)
from app.db.relational.repositories.message_repository import MessageRepository
from app.db.relational.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.chat.conversation_manager import ConversationManager
from app.modules.chat.service import ChatService
from app.modules.retrieval.dependencies import get_retrieval_service
from app.shared.llm import LLM

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.db.relational.models.conversation import Conversation
    from app.db.relational.models.user import User
    from app.modules.retrieval.service import RetrievalService

logger = logging.getLogger(__name__)


settings = get_settings()


def get_chat_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    retrieval_service: RetrievalService = Depends(get_retrieval_service),  # noqa: B008
) -> ChatService:
    return ChatService(
        conversation_repo=ConversationRepository(db),
        message_repo=MessageRepository(db),
        convesation_manager=ConversationManager(settings),
        retrieval_service=retrieval_service,
        llm=LLM(model=settings.vlm_model, api_key=settings.vlm_api_key),
        settings=settings,
    )


async def get_current_conv(
    conversation_id: UUID,
    user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Conversation:
    conversation_repo = ConversationRepository(db)
    conversation = await conversation_repo.get_by_id(conversation_id=conversation_id)
    if conversation.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden access to conversation",
        )
    return conversation
