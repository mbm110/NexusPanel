"""
Configuration and environment settings.
"""

import os
from pathlib import Path


class Settings:
    DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
    DATA_FILE = DATA_DIR / "nexus_state.json"
    SECRET_FILE = DATA_DIR / "nexus_secret.key"

    PORT = int(os.environ.get("PORT", 8000))
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_ADMIN_IDS = os.environ.get("TELEGRAM_ADMIN_IDS", "").strip()

    DEFAULT_PASSWORD = "NEXUSKING"