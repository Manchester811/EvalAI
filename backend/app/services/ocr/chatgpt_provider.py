"""ChatGPT vision provider adapter — keeps API key backend-only."""
import base64
from typing import Any
from .adapter import OCRProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # graceful if package not installed


class ChatGPTProvider(OCRProvider):
    """Uses OpenAI vision model to extract handwritten text from scanned sheets."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        if OpenAI is None:
            raise ImportError("openai package required; install with pip install openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract_text(self, image_path: str) -> list[dict[str, Any]]:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract handwritten answer text. Return JSON with keys 'text' (string) and 'confidence' (float 0-1)."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}},
                    ],
                }],
                max_tokens=2000,
            )
        # Parse JSON content from response; fall back to raw text if parsing fails
        content = response.choices[0].message.content or ""
        try:
            import json
            parsed = json.loads(content)
            return [{"text": str(parsed.get("text", content)), "confidence": float(parsed.get("confidence", 0.85))}]
        except Exception:
            return [{"text": content, "confidence": 0.85}]
