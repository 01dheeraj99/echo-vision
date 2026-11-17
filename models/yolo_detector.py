import os
from pathlib import Path
from ultralytics import YOLO
import cv2

from config.settings import BASE_DIR, YOLO_MODEL_NAME

class YOLODetector:
    """YOLOv8 Object Detection model wrapper."""

    def __init__(self, model_path: str = None):
        if not model_path:
            # Check local workspace first, then default
            local_weights = BASE_DIR / YOLO_MODEL_NAME
            model_path = str(local_weights) if local_weights.exists() else YOLO_MODEL_NAME

        print(f"[INFO] Initializing YOLO Detector ({model_path})...")
        self.model = YOLO(model_path)
        print("[INFO] YOLO Detector successfully loaded.")

    def detect_objects(self, image_path: str, conf_threshold: float = 0.35) -> list:
        """
        Run object detection on an image.
        Returns a list of dicts with label, confidence, and bounding box coordinates [x1, y1, x2, y2].
        """
        try:
            results = self.model(image_path, conf=conf_threshold, verbose=False)
            detections = []
            if results and len(results) > 0:
                result = results[0]
                names = result.names
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    label = names.get(cls_id, f"class_{cls_id}")
                    conf = round(float(box.conf[0].item()), 2)
                    xyxy = [int(v) for v in box.xyxy[0].tolist()]
                    detections.append({
                        "label": label,
                        "confidence": conf,
                        "box": xyxy
                    })
            return detections
        except Exception as e:
            print(f"[ERROR] Object detection failed: {e}")
            return []

    def get_summary_sentence(self, detections: list) -> str:
        """Constructs a readable English summary of detected objects and their counts."""
        if not detections:
            return "No prominent objects detected."

        counts = {}
        for det in detections:
            lbl = det["label"]
            counts[lbl] = counts.get(lbl, 0) + 1

        items = []
        for lbl, count in counts.items():
            if count == 1:
                items.append(f"1 {lbl}")
            else:
                items.append(f"{count} {lbl}s")

        if len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return ", ".join(items[:-1]) + f", and {items[-1]}"

    def annotate_image(self, image_path: str, detections: list, output_path: str) -> str:
        """Annotates image with bounding boxes and labels, saving to output_path."""
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        for det in detections:
            x1, y1, x2, y2 = det.get("box", [0, 0, 0, 0])
            label = det.get("label", "object")
            conf = det.get("confidence", 0.0)

            # Draw rectangle
            cv2.rectangle(img, (x1, y1), (x2, y2), (46, 204, 113), 2)
            caption = f"{label} {int(conf * 100)}%"
            (tw, th), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x1, max(0, y1 - 20)), (x1 + tw + 6, max(0, y1)), (46, 204, 113), -1)
            cv2.putText(img, caption, (x1 + 3, max(14, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        return output_path

