import io
from PIL import Image
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    # Initialize EasyOCR reader (lazy loading)
    _easyocr_reader = None
except ImportError:
    EASYOCR_AVAILABLE = False


class OCRService:
    def __init__(self):
        self.use_easyocr = EASYOCR_AVAILABLE
        if not TESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
            print("Warning: No OCR library available. Install pytesseract or easyocr.")
    
    async def extract_text(self, image_content: bytes) -> str:
        """Extract text from image using OCR"""
        if not TESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
            return ""
        
        try:
            image = Image.open(io.BytesIO(image_content))
            
            # Try EasyOCR first (more accurate), fallback to Tesseract
            if self.use_easyocr:
                return await self._extract_with_easyocr(image)
            elif TESSERACT_AVAILABLE:
                return await self._extract_with_tesseract(image)
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return ""
    
    async def _extract_with_tesseract(self, image: Image.Image) -> str:
        """Extract text using Tesseract OCR"""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Tesseract OCR Error: {str(e)}")
            return ""
    
    async def _extract_with_easyocr(self, image: Image.Image) -> str:
        """Extract text using EasyOCR"""
        global _easyocr_reader
        try:
            if _easyocr_reader is None:
                _easyocr_reader = easyocr.Reader(['en'], gpu=False)
            
            # Convert PIL image to numpy array
            import numpy as np
            img_array = np.array(image)
            
            results = _easyocr_reader.readtext(img_array)
            text = "\n".join([result[1] for result in results])
            return text.strip()
        except Exception as e:
            print(f"EasyOCR Error: {str(e)}")
            # Fallback to Tesseract if available
            if TESSERACT_AVAILABLE:
                return await self._extract_with_tesseract(image)
            return ""

