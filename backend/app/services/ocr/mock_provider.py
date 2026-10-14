from typing import List, Dict, Any
from app.services.ocr.adapter import OCRProvider


class MockOCRProvider(OCRProvider):
    """Mock provider available for dev (FR-06)."""

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        return [{'text': 'MOCK_TEXT', 'confidence': 1.0}]
