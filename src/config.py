import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

POLL_INTERVAL_MS = 3000

APP_WIDTH = 1280
APP_HEIGHT = 800


def validate_config():
    missing = []

    if not BACKEND_BASE_URL:
        missing.append("BACKEND_BASE_URL")

    if not FIREBASE_WEB_API_KEY:
        missing.append("FIREBASE_WEB_API_KEY")

    if not FIREBASE_PROJECT_ID:
        missing.append("FIREBASE_PROJECT_ID")

    if missing:
        raise RuntimeError(
            "Missing environment variable(s): "
            + ", ".join(missing)
            + ". Add them to your .env file."
        )