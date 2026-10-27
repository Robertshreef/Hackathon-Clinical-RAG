from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel


# ── Responses ─────────────────────────────────────────────────────────────────
class ConversationMetadata(BaseModel):
    "The metadata exposed to the front end"

    id: UUID
    name: str


class MessageMetadata(BaseModel):
    "The metadata exposed to the front end"

    role: str
    content: str


# class ChatResponse(BaseModel):
#     "The response model for the chat endpoint"

#     answer: str
#     sources: list[CitedSource] = Field(
#         default_factory=list,
#         description="Chunks cited by the agent, with document and page info",
#     )


class ChatResponse(BaseModel):
    answer: str
    sources: list[CitedSource]
    alert: EmergencyAlert | None = None


class EmergencyAlert(BaseModel):
    severity: Literal[
        "urgent", "emergency"
    ]  # e.g. "see a doctor soon" vs "call emergency services"
    message: str  # short, specific reason — not a diagnosis


class CitedSource(BaseModel):
    index: str
    content: str
    reason: str
    file_name: str
    starting_page: int
    end_page: int


class CitationMetaData(BaseModel):
    document_id: UUID
    starting_page: int
    end_page: int


class CitedSources(BaseModel):
    "A single retrieval chunk surfaced to the caller for citation display."

    inline_index: int  # the [N] number used inline in the answer text
    chunk_id: str
    document_id: str
    chunk_type: str | None = None  # "theory" or "solved_question"
    score: float
    full_content: str  # complete chunk text for hover display
    content_preview: str  # first 200 chars for quick display
    starting_page: int | None = None
    end_page: int | None = None
