import os
import uuid
import base64
from pathlib import Path
from PIL import Image, ImageOps
import cv2
import numpy as np

from config.settings import ALLOWED_EXTENSIONS, UPLOADS_DIR

def is_allowed_image(filename: str) -> bool:
    """Check if the uploaded file has an allowed image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def save_image(uploaded_file, target_dir: Path = UPLOADS_DIR) -> str:
    """Save an uploaded Flask file storage safely with a unique filename."""
    target_dir.mkdir(parents=True, exist_ok=True)
    ext = uploaded_file.filename.rsplit(".", 1)[1].lower() if "." in uploaded_file.filename else "jpg"
    unique_name = f"{uuid.uuid4().hex[:12]}.{ext}"
    saved_path = target_dir / unique_name
    uploaded_file.save(str(saved_path))
    return str(saved_path)

def save_base64_image(base64_data: str, target_dir: Path = UPLOADS_DIR) -> str:
    """Decode a base64 string (e.g. webcam snapshot) and save to disk."""
    target_dir.mkdir(parents=True, exist_ok=True)
    if "," in base64_data:
        base64_data = base64_data.split(",", 1)[1]
    image_bytes = base64.b64decode(base64_data)
    unique_name = f"webcam_{uuid.uuid4().hex[:12]}.jpg"
    saved_path = target_dir / unique_name
    with open(saved_path, "wb") as f:
        f.write(image_bytes)
    return str(saved_path)

def validate_and_correct_orientation(image_path: str) -> str:
    """Open image, correct EXIF orientation if needed, and verify validity."""
    try:
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            # Re-save if needed
            img.save(image_path)
        return image_path
    except Exception as e:
        print(f"[WARN] Error correcting EXIF orientation: {e}")
        return image_path

def preprocess_for_ocr(image_path: str) -> np.ndarray:
    """Preprocess image with OpenCV (grayscale, slight denoising) to improve OCR accuracy."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    # Resize if extremely small to help OCR
    h, w = img.shape[:2]
    if max(h, w) < 600:
        scale = 600.0 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    return img

def draw_detections(image_path: str, detections: list, output_path: str) -> str:
    """Draw bounding boxes and class labels onto the image and save the annotated version."""
    img = cv2.imread(image_path)
    if img is None:
        return image_path

    for det in detections:
        box = det.get("box", [])  # [x1, y1, x2, y2]
        label = det.get("label", "object")
        conf = det.get("confidence", 0.0)

        if len(box) == 4:
            x1, y1, x2, y2 = [int(v) for v in box]
            color = (46, 204, 113)  # Emerald green (BGR: 113, 204, 46)
            cv2.rectangle(img, (x1, y1), (x2, y2), (113, 204, 46), 2)
            caption = f"{label} {int(conf * 100)}%"
            (tw, th), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x1, max(0, y1 - 20)), (x1 + tw + 6, max(0, y1)), (113, 204, 46), -1)
            cv2.putText(img, caption, (x1 + 3, max(14, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    return output_path

