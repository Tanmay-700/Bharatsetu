import sys
import logging
from pathlib import Path
from app.core.config import settings

# Setup standard logging
log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("BharatSetu")
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Console handler with safe UTF-8 encoding
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
logger.addHandler(console_handler)

# File handler
try:
    log_path = settings.DATA_DIR / "app.log"
    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not initialize file log handler: {e}")
