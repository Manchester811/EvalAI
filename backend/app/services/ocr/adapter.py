from abc import ABC, abstractmethod
from typing import List, Dict, Any


class OCRProvider(ABC):
    """Abstract base class for OCR providers."""

    @abstractmethod
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from an image file.

        Args:
            image_path: Path to the image file

        Returns:
            List of dicts with 'text' and 'confidence' keys
            Example: [{'text': 'Hello world', 'confidence': 0.95}, ...]
        """
        pass


def get_ocr_provider() -> OCRProvider:
    """Factory function to get the configured OCR provider."""
    from app.core.config import settings

    provider_name = settings.OCR_PROVIDER.lower()

    if provider_name == 'paddleocr':
        from app.services.ocr.paddleocr_provider import PaddleOCRProvider
        return PaddleOCRProvider()
    elif provider_name == 'mock':
        from app.services.ocr.mock_provider import MockOCRProvider
        return MockOCRProvider()
    else:
        raise ValueError(f'Unknown OCR provider: {provider_name}')
