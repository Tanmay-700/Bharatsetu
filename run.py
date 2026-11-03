import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Automatically locate and add backend directory to Python path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.insert(0, str(BACKEND_DIR))
os.chdir(str(BACKEND_DIR))

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print(" Starting BharatSetu Backend Server...")
    print(f" Working Directory: {BACKEND_DIR}")
    print(" Docs URL: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=str(BACKEND_DIR)
    )
