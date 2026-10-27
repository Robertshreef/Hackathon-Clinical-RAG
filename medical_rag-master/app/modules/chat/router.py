from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.db.relational.models.conversation import Conversation
from app.db.relational.models.user import User
from app.db.relational.schemas import ConversationCreate, ConversationUpdate
from app.modules.auth.dependencies import get_current_user
from app.modules.chat.dependencies import (
    get_chat_service,
    get_current_conv,
)
from app.modules.chat.schemas import (
    ChatResponse,
    ConversationMetadata,
    MessageMetadata,
)

DATA_DIR = (Path(__file__).resolve().parents[3] / "data" / "src").resolve()

if TYPE_CHECKING:
    from app.modules.chat.service import ChatService


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/conversations",
    summary="create a new conversation",
    response_model=ConversationMetadata,
    status_code=status.HTTP_201_CREATED,
)
async def add_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationMetadata:
    response = await chat_service.add_conversation(user_id=user.id, data=data)
    return response


@chat_router.get(
    "/conversations",
    summary="list all conversations for the current user",
    response_model=list[ConversationMetadata],
    status_code=status.HTTP_200_OK,
)
async def list_conversations(
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> list[ConversationMetadata]:
    return await chat_service.list_conversations(user_id=user.id)


@chat_router.patch(
    "/conversations/{conversation_id}",
    summary="update conversation name",
    response_model=ConversationMetadata,
    status_code=status.HTTP_200_OK,
)
async def update_conversation(
    data: ConversationUpdate,
    conv: Conversation = Depends(get_current_conv),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationMetadata:
    return await chat_service.update_conversation(conv=conv, data=data)


@chat_router.delete(
    "/conversations/{conversation_id}",
    summary="delete conversation",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conv: Conversation = Depends(get_current_conv),
    chat_service: ChatService = Depends(get_chat_service),
) -> None:
    return await chat_service.delete_conversation(conv=conv)


@chat_router.post(
    "/conversations/{conversation_id}/messages",
    summary="Send a message and receive a RAG-grounded answer",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def send_message(
    query: str,
    conv: Conversation = Depends(get_current_conv),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.chat(conv=conv, query=query)


@chat_router.get(
    "/conversations/{conversation_id}/messages",
    summary="Fetch the full message history for a conversation",
    response_model=list[MessageMetadata],
    status_code=status.HTTP_200_OK,
)
async def get_history(
    conv: Conversation = Depends(get_current_conv),
    service: ChatService = Depends(get_chat_service),
) -> list[MessageMetadata]:
    return await service.list_messages(conv.id)


@chat_router.get(
    "/files/{file_name}",
    summary="Download a source document referenced in a citation",
)
async def download_reference_file(
    file_name: str,
    user: User = Depends(get_current_user),  # keep downloads behind auth
) -> FileResponse:
    candidate = (DATA_DIR / file_name).resolve()
    if DATA_DIR not in candidate.parents and candidate != DATA_DIR:
        raise HTTPException(status_code=400, detail="Invalid file name")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        candidate,
        filename=file_name,
        media_type="application/octet-stream",
    )
