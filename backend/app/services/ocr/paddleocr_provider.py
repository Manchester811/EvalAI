import os
from typing import List, Dict, Any
from app.services.ocr.adapter import OCRProvider
from app.core.config import settings


class PaddleOCRProvider(OCRProvider):
    """Placeholder/stub implementing OCRProvider using PaddleOCR or mock."""

    def __init__(self):
        # Credentials/config kept behind adapter; never exposed to browser
        self.provider_name = settings.OCR_PROVIDER
        self.api_key = os.getenv('PADDLE_API_KEY', '')

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """Stub: return mock results (or integrate PaddleOCR if available)."""
        # In production, use PaddleOCR here with self.api_key
        # For dev, return mock data to avoid external dependency
        return [
            {'text': 'Sample extracted text from ' + os.path.basename(image_path), 'confidence': 0.92}
        ]
