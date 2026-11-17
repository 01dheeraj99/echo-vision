import sys
import os
from pathlib import Path

# Auto-bootstrap: if invoked with global Python, automatically switch to project's virtual environment
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(project_dir, "venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
    import subprocess
    sys.exit(subprocess.call([venv_python] + sys.argv))

# Add project root to sys.path so imports resolve cleanly
sys.path.append(project_dir)

from models.pipeline import EchoVisionPipeline
from config.settings import SAMPLES_DIR

def run_test():
    sample_image = SAMPLES_DIR / "sample.jpeg"
    if not sample_image.exists():
        print(f"[ERROR] Sample image not found at {sample_image}")
        return

    print("=" * 60)
    print(" ECHOVISION MULTIMODAL PIPELINE TEST")
    print("=" * 60)
    print(f"Target Image: {sample_image}")

    pipeline = EchoVisionPipeline()
    result = pipeline.process_image(str(sample_image))

    print("\n" + "=" * 60)
    print(" PIPELINE RESULTS SUMMARY")
    print("=" * 60)
    print(f"Caption:         {result['caption']}")
    print(f"Detected Objects:{result['objects_summary']}")
    print(f"OCR Text:        '{result['ocr_text']}'")
    print(f"Full Narration:  {result['narration']}")
    print(f"Audio Output:    {result['audio_path']}")
    print(f"TTS Engine Used: {result['tts_engine']}")
    print(f"Annotated Image: {result['annotated_path']}")
    print(f"Elapsed Time:    {result['execution_time_seconds']}s")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
