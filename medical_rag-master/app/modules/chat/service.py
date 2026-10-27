from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING
from uuid import UUID

from app.db.relational.constants import MessageRole
from app.db.relational.models.conversation import Conversation
from app.db.relational.schemas import ConversationCreate, MessageCreate
from app.modules.chat.prompt import build_clinical_prompt, build_guardrail_prompt
from app.modules.chat.schemas import (
    ChatResponse,
    CitedSource,
    ConversationMetadata,
    EmergencyAlert,
    MessageMetadata,
)

if TYPE_CHECKING:
    from app.db.relational.models.message import Message
    from app.db.relational.repositories.conversation_repository import (
        ConversationRepository,
    )
    from app.db.relational.repositories.message_repository import MessageRepository
    from app.db.relational.schemas import ConversationUpdate
    from app.modules.chat.conversation_manager import ConversationManager
    from app.modules.retrieval.service import RetrievalService
    from app.shared.llm import LLM
    from app.shared.schemas import ChunkMeta


logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        convesation_manager: ConversationManager,
        retrieval_service: RetrievalService,
        llm: LLM,
        settings,
    ):
        self._conv_repo = conversation_repo
        self._message_repo = message_repo
        self._conv_manager = convesation_manager
        self._settings = settings
        self._retrieval_service = retrieval_service
        self._llm = llm

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    async def add_conversation(
        self, data: ConversationCreate, user_id: UUID
    ) -> ConversationMetadata:
        conv = await self._conv_repo.add(data=data, user_id=user_id)
        return ConversationMetadata(id=conv.id, name=conv.name)

    async def list_conversations(self, user_id: UUID) -> list[ConversationMetadata]:
        conversations = await self._conv_repo.get_all_by_user(user_id=user_id)
        return [ConversationMetadata(id=c.id, name=c.name) for c in conversations]

    async def update_conversation(
        self, data: ConversationUpdate, conv: Conversation
    ) -> ConversationMetadata:
        conv = await self._conv_repo.update(data=data, conversation=conv)
        return ConversationMetadata(id=conv.id, name=conv.name)

    async def delete_conversation(self, conv: Conversation) -> None:
        await self._conv_repo.delete(conv)

    async def list_messages(self, id: UUID) -> list[MessageMetadata]:
        messages = await self._message_repo.get_all_by_conversation(id)
        return [MessageMetadata(role=m.role, content=m.content) for m in messages]

    # ------------------------------------------------------------------
    # chat
    # ------------------------------------------------------------------

    async def chat(self, conv: Conversation, query: str) -> ChatResponse:
        raw_history = await self._message_repo.get_all_by_conversation(conv.id)
        trimmed_history = self._conv_manager.trim_history(raw_history)
        history = self._format_chat_history(trimmed_history)

        # -------------------------------------------------------------
        # STEP 1: Guardrail & Query Normalization Call
        # -------------------------------------------------------------
        guard_prompt = build_guardrail_prompt(user_query=query, history=history)
        guard_response = await self._llm.complete(prompt=guard_prompt)

        if "<<<STATUS: GREETING>>>" in guard_response:
            answer = "Hello! How can I assist you today regarding preeclampsia or hypertensive pregnancy health topics?"
            return await self._save_and_respond(conv, query, answer)

        if "<<<STATUS: REJECTED>>>" in guard_response:
            answer = "I am a medical assistant specialized in preeclampsia and pregnancy-related hypertensive disorders. I can only assist with questions related to these clinical topics."
            return await self._save_and_respond(conv, query, answer)

        # Extract rewritten query if present; fall back to original
        query_match = re.search(
            r"<rewritten_query>\s*(.*?)\s*</rewritten_query>",
            guard_response,
            re.DOTALL,
        )
        effective_query = query_match.group(1).strip() if query_match else query

        # -------------------------------------------------------------
        # STEP 2: Retrieval & Clinical Response Generation Call
        # -------------------------------------------------------------
        retrieved_chunks = await self._retrieval_service.retrieve(query=effective_query)
        context = self._format_retrieved_context(retrieved_chunks)

        clinical_prompt = build_clinical_prompt(
            user_query=effective_query, context=context, history=history
        )
        raw_answer = await self._llm.complete(prompt=clinical_prompt)

        # -------------------------------------------------------------
        # STEP 3: Emergency Detection & Citation Parsing
        # -------------------------------------------------------------
        alert = None
        alert_pattern = (
            r'<<<EMERGENCY_ALERT:\s*severity="([^"]+)"\s*message="([^"]+)"\s*>>>'
        )
        alert_match = re.search(alert_pattern, raw_answer)

        if alert_match:
            severity, message = alert_match.groups()
            alert = EmergencyAlert(
                severity=severity,  # "urgent" | "emergency" # type: ignore
                message=message,
            )
            # Remove alert tag from public body answer
            raw_answer = re.sub(alert_pattern, "", raw_answer).strip()

        # Save conversation history
        await self._message_repo.add(
            data=MessageCreate(role=MessageRole.user, content=query),
            conversation_id=conv.id,
        )
        await self._message_repo.add(
            data=MessageCreate(role=MessageRole.assistant, content=raw_answer),
            conversation_id=conv.id,
        )

        chat_response = self._process_llm_response(raw_answer, retrieved_chunks)
        chat_response.alert = alert
        return chat_response

    async def _save_and_respond(
        self, conv: Conversation, query: str, answer: str
    ) -> ChatResponse:
        """Helper for early termination responses (greetings / off-topic)."""
        await self._message_repo.add(
            data=MessageCreate(role=MessageRole.user, content=query),
            conversation_id=conv.id,
        )
        await self._message_repo.add(
            data=MessageCreate(role=MessageRole.assistant, content=answer),
            conversation_id=conv.id,
        )
        return ChatResponse(answer=answer, sources=[], alert=None)

    def _format_retrieved_context(self, chunks: list[ChunkMeta]) -> str:
        if not chunks:
            return "No relevant context retrieved."

        formatted_blocks = []
        for chunk in chunks:
            block = (
                f"[{chunk.index}] Source File: {chunk.file_name} "
                f"(Pages {chunk.starting_page}-{chunk.end_page})\n"
                f"Content: {chunk.content.strip()}"
            )
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)

    def _format_chat_history(self, messages: list[Message]) -> str:
        if not messages:
            return "No prior conversation history."

        history_lines = []
        for msg in messages:
            # Access role enum value (e.g., 'user', 'assistant') and content text
            role_name = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            history_lines.append(f"{role_name.capitalize()}: {msg.content.strip()}")

        return "\n".join(history_lines)

    def _process_llm_response(
        self, response: str, retrieved_chunks: list[ChunkMeta]
    ) -> ChatResponse:
        chunk_map = {chunk.index: chunk for chunk in retrieved_chunks}

        citation_pattern = r"([^.!?\n]+[\.!?]?)\s*((?:\[\d+(?:\s*,\s*\d+)*\])+)"
        matches = re.findall(citation_pattern, response)

        seen_indices = {}
        cited_sources: list[CitedSource] = []

        for statement, citation_block in matches:
            raw_indices = [int(idx) for idx in re.findall(r"\d+", citation_block)]

            for raw_idx in raw_indices:
                if raw_idx in chunk_map and raw_idx not in seen_indices:
                    seq_id = len(seen_indices) + 1
                    seen_indices[raw_idx] = seq_id

                    chunk = chunk_map[raw_idx]
                    cited_sources.append(
                        CitedSource(
                            index=f"[{seq_id}]",
                            content=chunk.content,
                            reason=f"Supports claim: '{statement.strip()}'",
                            file_name=chunk.file_name,
                            starting_page=chunk.starting_page,
                            end_page=chunk.end_page,
                        )
                    )

        def replace_tag(match):
            raw_idx = int(match.group(1))
            if raw_idx in seen_indices:
                return f"[{seen_indices[raw_idx]}]"
            return ""

        clean_answer = re.sub(r"\[(\d+)\]", replace_tag, response)

        return ChatResponse(answer=clean_answer.strip(), sources=cited_sources)
