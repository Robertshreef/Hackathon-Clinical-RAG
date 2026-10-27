from __future__ import annotations

import base64
import io

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image as PILImage


class VLM:
    def __init__(self, model: str, api_key: str):
        self._vlm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
        )

    def call_vlm_with_prompt_and_image(
        self,
        prompt_text: str,
        img: PILImage.Image,
    ) -> str:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_data = f"data:image/png;base64,{img_str}"

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": image_data}},
            ]
        )

        response = self._vlm.invoke([message])

        if isinstance(response.content, list):
            text = "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text = str(response.content)

        return text

    def call_vlm_with_prompt_and_images(
        self,
        prompt_text: str,
        img: list[PILImage.Image],
    ) -> str:
        # 1. Standardize input to always be a list of images
        images = img if isinstance(img, list) else [img]

        # 2. Build the message content with the text prompt first
        message_content = [{"type": "text", "text": prompt_text}]

        # 3. Loop through all images, convert to base64, and append block elements
        for image in images:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            image_data = f"data:image/png;base64,{img_str}"

            message_content.append(
                {"type": "image_url", "image_url": {"url": image_data}}
            )  # type: ignore

        # 4. Invoke the model with the combined content payload
        message = HumanMessage(content=message_content)  # type: ignore
        response = self._vlm.invoke([message])

        # 5. Safely parse and extract response text
        if isinstance(response.content, list):
            text = "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text = str(response.content)

        return text
