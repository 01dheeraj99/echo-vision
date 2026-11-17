# EchoVision 👁️🔊

> **An AI-powered multimodal image-to-speech assistive technology system designed for visually impaired and low-vision users.**

EchoVision transforms visual imagery into natural, structured spoken narrations in real-time. It leverages state-of-the-art vision models to synthesize image captioning, object detection, and optical character recognition (OCR) into coherent accessibility narrations.

---

## 🌟 Key Features

- **Salesforce BLIP Image Captioning:** Produces descriptive, context-aware natural language descriptions of the scene.
- **YOLOv8 Real-Time Object Detection:** Identifies foreground and background objects, counts, and spatial relationships.
- **EasyOCR Embedded Text Extraction:** Reads signage, product labels, documents, and text within the scene.
- **Dual Text-to-Speech (TTS) Engine:**
  - Online high-fidelity speech synthesis via **Google Text-to-Speech (gTTS)**.
  - Transparent offline fallback via **pyttsx3 (SAPI5)** when network is unavailable.
  - In-browser **Web Speech API** integration for instant, zero-latency device-native playback.
- **WCAG 2.1 AAA Accessibility Web Interface:**
  - One-click **High Contrast Mode** with optimized contrast ratios.
  - Scalable font sizing.
  - Screen reader live announcements (`aria-live="polite"`).
  - Global keyboard shortcuts (`U` = Upload, `C` = Camera, `Space` = Play/Pause Audio, `S` = Sample).
  - Live webcam capture directly in the browser.
  - Drag-and-drop file upload with visual feedback.
  - Bounding-box visual highlights toggle.

---

## 🏗️ Project Architecture

```
EchoVision/
├── app.py                      # Flask web application & REST API endpoints
├── requirements.txt            # Python dependencies
├── yolov8n.pt                  # YOLOv8 nano pretrained model weights
├── config/
│   └── settings.py             # Global configurations, directories & hyperparameters
├── models/
│   ├── blip_loader.py          # Salesforce BLIP captioning model wrapper
│   ├── yolo_detector.py        # Ultralytics YOLOv8 object detector & visual annotator
│   ├── ocr_engine.py           # EasyOCR text extraction engine
│   └── pipeline.py             # EchoVisionPipeline unified orchestrator
├── utils/
│   ├── audio_utils.py          # Speech synthesis (gTTS + pyttsx3 fallback + narration builder)
│   └── image_utils.py          # Image validation, preprocessing, webcam base64 decoding & drawing
├── templates/
│   ├── index.html              # Accessible web interface (WCAG 2.1 AAA)
│   └── result.html             # Analysis results template
├── static/
│   ├── css/style.css           # Styling, themes & high-contrast mode
│   └── js/script.js            # Frontend interactivity, webcam stream, audio controls & shortcuts
├── scripts/
│   └── test_pipeline.py        # End-to-end command-line pipeline test runner
├── tests/
│   ├── test_models.py          # Unit tests for models & utilities
│   └── test_routes.py          # Integration tests for Flask routes
└── data/
    ├── samples/                # Sample test images
    ├── uploads/                # User uploaded images
    └── outputs/                # Generated audio (.mp3/.wav) and annotated images
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 to 3.12
- Windows, macOS, or Linux

### 2. Environment Setup
```powershell
# Clone or navigate to the repository
cd EchoVision

# Activate the virtual environment
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Pipeline Test (CLI)
Verify the core vision and audio pipeline from the command line:
```powershell
python scripts/test_pipeline.py
```

### 4. Run Automated Tests
Execute the unit and route test suite:
```powershell
python -m unittest discover -s tests -v
```

### 5. Launch the Web Application

#### Option A: Production WSGI Server (Recommended - No Warnings)
```powershell
python wsgi.py
# or
python app.py --prod
```

#### Option B: Development Server (With auto-reload)
```powershell
python app.py
```

Then open your browser to:
```
http://127.0.0.1:5000
```

---

## 📡 REST API Reference

### `POST /analyze`
Analyzes an image and returns structured JSON with audio and visual links.

**Request:** `multipart/form-data` with `image` file OR `application/json` with `image_base64`:
```json
{
  "image_base64": "data:image/jpeg;base64,..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "caption": "a cup of coffee sitting on a wooden table",
  "objects": [
    { "label": "cup", "confidence": 0.92, "box": [120, 80, 310, 290] },
    { "label": "bowl", "confidence": 0.74, "box": [45, 110, 390, 350] }
  ],
  "objects_summary": "1 bowl and 1 cup",
  "ocr_text": "",
  "narration": "Image summary: A cup of coffee sitting on a wooden table. Detected items in view: 1 bowl and 1 cup.",
  "audio_url": "/audio/audio_e4323f05d1.mp3",
  "image_url": "/uploads/4deb876562e9.jpeg",
  "annotated_image_url": "/outputs/annotated_e4323f05d1.jpg",
  "tts_engine": "gtts",
  "execution_time_seconds": 3.4
}
```

### `GET /health`
Returns system health, GPU availability, and directory status.

---

## ♿ Accessibility Features

- **High Contrast:** Press the **High Contrast** button or toggle via `Alt + H` to switch to high-visibility black-and-yellow styling.
- **Font Scaling:** Increase or reset base typography size on demand.
- **Keyboard Navigation:**
  - `U` &mdash; Open file upload dialogue
  - `C` &mdash; Open live webcam scanner
  - `Space` &mdash; Play or pause audio narration
  - `S` &mdash; Run instantaneous analysis on sample image

---

## 📜 License
MIT License. Built for accessibility and inclusive AI assistance.
