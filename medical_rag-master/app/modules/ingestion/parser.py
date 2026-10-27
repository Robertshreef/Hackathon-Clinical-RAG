from __future__ import annotations

import io
import re
from pathlib import Path
from typing import TYPE_CHECKING

import fitz
from PIL import Image as PILImage

from app.modules.ingestion.prompt import build_prompt
from app.shared.schemas import ChunkMeta

if TYPE_CHECKING:
    from app.shared.vlm import VLM


def chunk_output(
    raw_text: str,
    file_name: str,
    existing_chunks: list[ChunkMeta],
    page_number: int,
    index: int,
) -> int:
    if "<<<SKIP_PAGE>>>" in raw_text:
        return index

    chunk_pattern = r"(<<<START>>>|<<<CONTINUE>>>)(.*?)(?:<<<END>>>)"
    raw_chunks = re.findall(chunk_pattern, raw_text, re.DOTALL)

    for tag, chunk_body in raw_chunks:
        chunk_content = chunk_body.strip()

        if tag == "<<<CONTINUE>>>" and existing_chunks:
            existing_chunks[-1].content += " " + chunk_content
            existing_chunks[-1].end_page = page_number
        else:
            chunk = ChunkMeta(
                index=index,
                file_name=file_name,
                starting_page=page_number,
                end_page=page_number,
                content=chunk_content,
            )
            existing_chunks.append(chunk)
            index += 1

    return index


class PdfParser:
    def __init__(self, vlm: VLM):
        self.vlm = vlm

    def load(self, file_path: Path) -> list[ChunkMeta]:
        index = 1
        prev_chunk = ""
        chunks: list[ChunkMeta] = []

        docs = fitz.open(file_path)

        for page_no, page in enumerate(docs, start=1):  # type: ignore
            pix = page.get_pixmap(dpi=150)
            img = PILImage.open(io.BytesIO(pix.tobytes("png")))

            raw_text = self.vlm.call_vlm_with_prompt_and_image(
                build_prompt(prev_chunk), img
            )

            index = chunk_output(
                raw_text=raw_text,
                file_name=file_path.name,
                existing_chunks=chunks,
                page_number=page_no,
                index=index,
            )

            prev_chunk = chunks[-1].content if chunks else ""

        return chunks
