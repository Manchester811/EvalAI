"""Google Gemini vision provider adapter — keeps API key backend-only."""
import base64
import json
from typing import Any
from .adapter import OCRProvider

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # graceful if package not installed


class GeminiProvider(OCRProvider):
    """Uses Google Gemini vision model to extract handwritten text from scanned sheets."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        if genai is None:
            raise ImportError("google-genai package required; install with pip install google-genai")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract_text(self, image_path: str) -> list[dict[str, Any]]:
        with open(image_path, "rb") as f:
            image_bytes = base64.b64encode(f.read()).decode()

        mime = "image/png"
        if image_path.lower().endswith((".jpg", ".jpeg")):
            mime = "image/jpeg"
        elif image_path.lower().endswith(".webp"):
            mime = "image/webp"

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part(text="Extract handwritten answer text. Return JSON with keys 'text' (string) and 'confidence' (float 0-1)."),
                types.Part(inline_data=types.InlineData(mime_type=mime, data=image_bytes)),
            ],
        )
        content = response.text or ""
        try:
            parsed = json.loads(content)
            return [{"text": str(parsed.get("text", content)), "confidence": float(parsed.get("confidence", 0.85))}]
        except Exception:
            return [{"text": content, "confidence": 0.85}]