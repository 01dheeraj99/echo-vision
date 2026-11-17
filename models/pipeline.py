import os
import time
import uuid
from pathlib import Path

from config.settings import OUTPUTS_DIR, UPLOADS_DIR
from models.blip_loader import BLIPCaptioner
from models.ocr_engine import OCREngine
from models.yolo_detector import YOLODetector
from utils.audio_utils import build_accessible_narration, text_to_speech

class EchoVisionPipeline:
    """
    Unified multimodal AI pipeline orchestrator.
    Combines Salesforce BLIP (captioning), Ultralytics YOLOv8 (object detection),
    EasyOCR (text extraction), and Text-to-Speech (accessibility narration).
    """

    _instance = None

    def __init__(self, load_models: bool = True):
        self.blip = None
        self.yolo = None
        self.ocr = None
        if load_models:
            self.load_all_models()

    @classmethod
    def get_instance(cls):
        """Singleton accessor to prevent reloading heavy models multiple times."""
        if cls._instance is None:
            cls._instance = cls(load_models=True)
        return cls._instance

    def load_all_models(self):
        """Initialize all three vision models."""
        print("[PIPELINE] Loading all vision models into memory...")
        start = time.time()
        self.blip = BLIPCaptioner()
        self.yolo = YOLODetector()
        self.ocr = OCREngine()
        print(f"[PIPELINE] All models loaded in {time.time() - start:.2f}s")

    def process_image(
        self,
        image_path: str,
        generate_audio: bool = True,
        output_dir: Path = OUTPUTS_DIR,
        annotate: bool = True
    ) -> dict:
        """
        Runs the complete EchoVision accessibility analysis pipeline on an image.
        """
        start_time = time.time()
        output_dir.mkdir(parents=True, exist_ok=True)
        file_id = uuid.uuid4().hex[:10]

        # 1. Step 1: Image Captioning (BLIP)
        print(f"[PIPELINE] Step 1: Generating caption for {image_path}...")
        caption = self.blip.generate_caption(image_path)
        print(f"[PIPELINE] Caption: {caption}")

        # 2. Step 2: Object Detection (YOLO)
        print("[PIPELINE] Step 2: Detecting objects...")
        detected_objects = self.yolo.detect_objects(image_path)
        objects_summary = self.yolo.get_summary_sentence(detected_objects)
        print(f"[PIPELINE] Objects: {objects_summary}")

        # 3. Step 3: Optical Character Recognition (EasyOCR)
        print("[PIPELINE] Step 3: Extracting embedded text...")
        ocr_text = self.ocr.extract_text(image_path)
        print(f"[PIPELINE] OCR Text: '{ocr_text}'")

        # 4. Step 4: Build Accessible Narration
        narration = build_accessible_narration(
            caption=caption,
            objects=detected_objects,
            ocr_text=ocr_text
        )
        print(f"[PIPELINE] Narration: {narration}")

        # 5. Step 5: Text-to-Speech
        audio_filename = None
        audio_path = None
        tts_engine_used = None
        if generate_audio:
            print("[PIPELINE] Step 5: Generating speech audio...")
            audio_filename = f"audio_{file_id}.mp3"
            audio_path = str(output_dir / audio_filename)
            tts_res = text_to_speech(narration, audio_path)
            # If pyttsx3 generated a .wav fallback, adjust path
            audio_path = tts_res.get("output_path", audio_path)
            audio_filename = os.path.basename(audio_path)
            tts_engine_used = tts_res.get("engine", "unknown")

        # 6. Step 6: Annotated Image
        annotated_filename = None
        annotated_path = None
        if annotate and detected_objects:
            annotated_filename = f"annotated_{file_id}.jpg"
            annotated_path = str(output_dir / annotated_filename)
            self.yolo.annotate_image(image_path, detected_objects, annotated_path)

        total_time = round(time.time() - start_time, 2)
        print(f"[PIPELINE] Processing completed in {total_time}s")

        return {
            "success": True,
            "caption": caption,
            "objects": detected_objects,
            "objects_summary": objects_summary,
            "ocr_text": ocr_text,
            "narration": narration,
            "audio_filename": audio_filename,
            "audio_path": audio_path,
            "tts_engine": tts_engine_used,
            "annotated_filename": annotated_filename,
            "annotated_path": annotated_path,
            "execution_time_seconds": total_time
        }

