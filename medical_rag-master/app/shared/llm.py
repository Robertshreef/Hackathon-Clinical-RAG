from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

_ROLE_TO_LC = {
    "system": HumanMessage,  # Gemini has no system message type
    "user": HumanMessage,
    "assistant": AIMessage,
}


class LLM:
    def __init__(self, model: str, api_key: str):
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
        )

    async def complete(self, prompt: str) -> str:
        response = await self._llm.ainvoke(prompt)

        if isinstance(response.content, list):
            text = "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text = response.content

        return text
