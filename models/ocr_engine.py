import easyocr
from config.settings import OCR_LANGUAGES, USE_GPU_OCR

class OCREngine:
    """EasyOCR Engine for optical character recognition on images."""

    def __init__(self, languages: list = None, gpu: bool = None):
        self.languages = languages or OCR_LANGUAGES
        self.gpu = USE_GPU_OCR if gpu is None else gpu
        print(f"[INFO] Initializing EasyOCR Engine (languages={self.languages}, gpu={self.gpu})...")
        self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
        print("[INFO] EasyOCR Engine successfully loaded.")

    def extract_text(self, image_path: str, min_confidence: float = 0.25) -> str:
        """
        Runs OCR on image and returns detected text as a single cleaned string.
        """
        try:
            results = self.reader.readtext(image_path)
            # Filter low confidence predictions
            valid_words = [res[1].strip() for res in results if len(res) > 2 and res[2] >= min_confidence]
            extracted_text = " ".join([w for w in valid_words if w])
            return extracted_text.strip()
        except Exception as e:
            print(f"[ERROR] OCR text extraction failed: {e}")
            return ""

    def read_details(self, image_path: str, min_confidence: float = 0.25) -> list:
        """
        Returns structured list of OCR detections with bounding boxes and confidence scores.
        """
        try:
            raw_results = self.reader.readtext(image_path)
            detections = []
            for item in raw_results:
                if len(item) == 3:
                    box, text, score = item
                    if score >= min_confidence and text.strip():
                        detections.append({
                            "box": box,
                            "text": text.strip(),
                            "confidence": round(float(score), 2)
                        })
            return detections
        except Exception as e:
            print(f"[ERROR] OCR details read failed: {e}")
            return []
