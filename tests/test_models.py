import unittest
import os
from pathlib import Path
from PIL import Image

from config.settings import BASE_DIR, SAMPLES_DIR, OUTPUTS_DIR
from utils.image_utils import is_allowed_image
from utils.audio_utils import sanitize_text_for_speech, build_accessible_narration
from models.yolo_detector import YOLODetector

class TestEchoVisionModels(unittest.TestCase):
    
    def test_allowed_extensions(self):
        self.assertTrue(is_allowed_image("photo.jpg"))
        self.assertTrue(is_allowed_image("image.png"))
        self.assertTrue(is_allowed_image("scan.webp"))
        self.assertFalse(is_allowed_image("script.py"))
        self.assertFalse(is_allowed_image("document.pdf"))

    def test_sanitize_text(self):
        raw = "  Hello   world \n  this is   a test. "
        clean = sanitize_text_for_speech(raw)
        self.assertEqual(clean, "Hello world this is a test.")

    def test_narration_builder(self):
        caption = "a coffee cup on a table"
        objects = [{"label": "cup", "confidence": 0.95}, {"label": "bowl", "confidence": 0.70}]
        ocr = "Cafe Mocha"
        narration = build_accessible_narration(caption, objects, ocr)

        self.assertIn("A coffee cup on a table.", narration)
        self.assertIn("1 cup and 1 bowl", narration)
        self.assertIn("Cafe Mocha", narration)

    def test_yolo_summary_sentence(self):
        detector = YOLODetector.__new__(YOLODetector)
        detections = [
            {"label": "dog", "confidence": 0.9},
            {"label": "dog", "confidence": 0.85},
            {"label": "frisbee", "confidence": 0.92}
        ]
        summary = detector.get_summary_sentence(detections)
        self.assertEqual(summary, "2 dogs and 1 frisbee")

        empty_summary = detector.get_summary_sentence([])
        self.assertEqual(empty_summary, "No prominent objects detected.")

if __name__ == "__main__":
    unittest.main()

