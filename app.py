import os
import sys

# Auto-bootstrap: if invoked with global Python, automatically switch to project's virtual environment
project_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(project_dir, "venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
    import subprocess
    sys.exit(subprocess.call([venv_python] + sys.argv))

import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, flash

from config.settings import (
    BASE_DIR, UPLOADS_DIR, OUTPUTS_DIR, SAMPLES_DIR,
    HOST, PORT, DEBUG, SECRET_KEY, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS
)
from utils.image_utils import is_allowed_image, save_image, save_base64_image
from models.pipeline import EchoVisionPipeline

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(UPLOADS_DIR)
app.config["OUTPUTS_FOLDER"] = str(OUTPUTS_DIR)

# Pipeline instance (lazy initialized)
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = EchoVisionPipeline.get_instance()
    return _pipeline

# In-memory storage for non-JS form submissions
JOB_RESULTS = {}

@app.route("/")
def index():
    """Main accessible user interface."""
    # Check for available sample images
    samples = []
    if SAMPLES_DIR.exists():
        for f in SAMPLES_DIR.iterdir():
            if f.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS:
                samples.append(f.name)
    return render_template("index.html", samples=samples)

@app.route("/analyze", methods=["POST"])
def analyze_image():
    """
    Asynchronous JSON endpoint for image analysis.
    Accepts file upload or base64 snapshot from webcam.
    """
    saved_path = None
    original_filename = None

    try:
        # Check if multipart file upload
        if "image" in request.files and request.files["image"].filename:
            file = request.files["image"]
            if not is_allowed_image(file.filename):
                return jsonify({
                    "success": False,
                    "error": f"Invalid image format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
                }), 400
            original_filename = file.filename
            saved_path = save_image(file, UPLOADS_DIR)

        # Check if base64 webcam capture
        elif request.is_json and "image_base64" in request.json:
            b64_str = request.json["image_base64"]
            saved_path = save_base64_image(b64_str, UPLOADS_DIR)
            original_filename = os.path.basename(saved_path)

        # Check form data base64
        elif "image_base64" in request.form and request.form["image_base64"]:
            b64_str = request.form["image_base64"]
            saved_path = save_base64_image(b64_str, UPLOADS_DIR)
            original_filename = os.path.basename(saved_path)

        # Check if sample name provided
        elif request.is_json and "sample_name" in request.json:
            sample_file = SAMPLES_DIR / request.json["sample_name"]
            if sample_file.exists():
                saved_path = str(sample_file)
                original_filename = sample_file.name

        if not saved_path or not os.path.exists(saved_path):
            return jsonify({"success": False, "error": "No valid image provided for processing."}), 400

        # Execute analysis pipeline
        pipeline = get_pipeline()
        result = pipeline.process_image(saved_path)

        # Build public URLs
        audio_url = f"/audio/{result['audio_filename']}" if result.get("audio_filename") else None
        annotated_url = f"/outputs/{result['annotated_filename']}" if result.get("annotated_filename") else None
        
        # Determine image URL (upload vs sample)
        if str(SAMPLES_DIR) in saved_path:
            image_url = f"/samples/{os.path.basename(saved_path)}"
        else:
            image_url = f"/uploads/{os.path.basename(saved_path)}"

        response_data = {
            "success": True,
            "filename": original_filename,
            "caption": result["caption"],
            "objects": result["objects"],
            "objects_summary": result["objects_summary"],
            "ocr_text": result["ocr_text"],
            "narration": result["narration"],
            "audio_url": audio_url,
            "image_url": image_url,
            "annotated_image_url": annotated_url,
            "tts_engine": result.get("tts_engine"),
            "execution_time_seconds": result["execution_time_seconds"]
        }
        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def form_upload():
    """Standard HTML form submission route with redirect to /result/<task_id>."""
    if "image" not in request.files or not request.files["image"].filename:
        flash("Please select an image file to upload.", "error")
        return redirect(url_for("index"))

    file = request.files["image"]
    if not is_allowed_image(file.filename):
        flash(f"Invalid image format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}", "error")
        return redirect(url_for("index"))

    try:
        saved_path = save_image(file, UPLOADS_DIR)
        pipeline = get_pipeline()
        result = pipeline.process_image(saved_path)

        task_id = uuid.uuid4().hex[:12]
        JOB_RESULTS[task_id] = {
            "result": result,
            "image_url": f"/uploads/{os.path.basename(saved_path)}",
            "audio_url": f"/audio/{result['audio_filename']}" if result.get("audio_filename") else None,
            "annotated_url": f"/outputs/{result['annotated_filename']}" if result.get("annotated_filename") else None
        }
        return redirect(url_for("view_result", task_id=task_id))

    except Exception as e:
        flash(f"Failed to process image: {e}", "error")
        return redirect(url_for("index"))

@app.route("/result/<task_id>")
def view_result(task_id):
    """View results page for a completed analysis task."""
    job = JOB_RESULTS.get(task_id)
    if not job:
        flash("Analysis result expired or not found.", "warning")
        return redirect(url_for("index"))
    return render_template("result.html", task_id=task_id, job=job)

@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve generated audio narration file with caching headers."""
    return send_from_directory(str(OUTPUTS_DIR), filename)

@app.route("/uploads/<filename>")
def serve_upload(filename):
    """Serve uploaded user image."""
    return send_from_directory(str(UPLOADS_DIR), filename)

@app.route("/outputs/<filename>")
def serve_output(filename):
    """Serve generated annotated image."""
    return send_from_directory(str(OUTPUTS_DIR), filename)

@app.route("/samples/<filename>")
def serve_sample(filename):
    """Serve sample gallery image."""
    return send_from_directory(str(SAMPLES_DIR), filename)

@app.route("/health")
def health_check():
    """Health check endpoint reporting system readiness and hardware."""
    import torch
    return jsonify({
        "status": "healthy",
        "app": "EchoVision",
        "version": "1.0.0",
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "directories": {
            "uploads": os.path.exists(UPLOADS_DIR),
            "outputs": os.path.exists(OUTPUTS_DIR),
            "samples": os.path.exists(SAMPLES_DIR)
        }
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"success": False, "error": "File size exceeds the 16MB limit."}), 413

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/audio") or request.path.startswith("/uploads"):
        return jsonify({"success": False, "error": "Requested file not found."}), 404
    return render_template("index.html", error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": "Internal server error occurred."}), 500

if __name__ == "__main__":
    import sys
    if "--prod" in sys.argv or os.environ.get("FLASK_ENV") == "production":
        try:
            from waitress import serve
            print("=" * 65)
            print(" [PROD] Starting EchoVision Production WSGI Server (Waitress)")
            print(f" [URL]  http://127.0.0.1:{PORT} (Host: {HOST})")
            print("=" * 65)
            serve(app, host=HOST, port=PORT, threads=4)
        except ImportError:
            print("[WARN] 'waitress' not found. Falling back to development server.")
            app.run(host=HOST, port=PORT, debug=DEBUG)
    else:
        print("=" * 65)
        print(" [DEV] Starting EchoVision Development Server")
        print(f" [URL] http://127.0.0.1:{PORT}")
        print(" [TIP] To run without dev warning, use: python wsgi.py or python app.py --prod")
        print("=" * 65)
        app.run(host=HOST, port=PORT, debug=DEBUG)

