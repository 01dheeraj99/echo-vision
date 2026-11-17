import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
OUTPUTS_DIR = DATA_DIR / "outputs"
UPLOADS_DIR = DATA_DIR / "uploads"

# Ensure runtime directories exist
for directory in [DATA_DIR, SAMPLES_DIR, OUTPUTS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model Settings
BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-base"
YOLO_MODEL_NAME = "yolov8n.pt"
OCR_LANGUAGES = ["en"]

# Performance & Hardware
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_GPU_OCR = torch.cuda.is_available()

# TTS Settings
DEFAULT_TTS_ENGINE = "auto"  # 'auto' tries gTTS (online) first, falls back to pyttsx3 (offline)
TTS_LANGUAGE = "en"
PYTTSX3_RATE = 150  # Words per minute for speech rate
PYTTSX3_VOLUME = 1.0

# Flask App Configuration
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "echovision-accessibility-secret-key-2026")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "gif"}

