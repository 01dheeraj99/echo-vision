"""
Production WSGI server entrypoint for EchoVision.
Powered by Waitress (production-grade pure-Python WSGI server).
"""
import os
import sys

# Auto-bootstrap: if invoked with global Python, automatically switch to project's virtual environment
project_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(project_dir, "venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
    import subprocess
    sys.exit(subprocess.call([venv_python] + sys.argv))

from app import app
from config.settings import HOST, PORT

def run():
    try:
        from waitress import serve
    except ImportError:
        print("[ERROR] 'waitress' package is not installed. Run: pip install waitress")
        sys.exit(1)

    print("=" * 65)
    print(" ECHOVISION PRODUCTION WSGI SERVER (Waitress)")
    print(f" URL:     http://127.0.0.1:{PORT}")
    print(f" Host:    {HOST}:{PORT}")
    print(" Threads: 4 concurrent worker threads")
    print(" Status:  Production-Ready (No development server warning)")
    print("=" * 65)

    # Run production WSGI server
    serve(app, host=HOST, port=PORT, threads=4)

if __name__ == "__main__":
    run()
