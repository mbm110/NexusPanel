"""
Configuration and environment settings.
"""

import os
import secrets
from pathlib import Path


class Settings:
    DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
    DATA_FILE = DATA_DIR / "nexus_state.json"
    SECRET_FILE = DATA_DIR / "nexus_secret.key"

    PORT = int(os.environ.get("PORT", 8000))

    RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_ADMIN_IDS = os.environ.get("TELEGRAM_ADMIN_IDS", "").strip()

    DEFAULT_PASSWORD = "NEXUSKING"

    @property
    def secret(self) -> str:
        """Load or generate a persistent secret for password hashing."""
        if os.environ.get("SECRET_KEY"):
            return os.environ["SECRET_KEY"]
        if self.SECRET_FILE.exists():
            return self.SECRET_FILE.read_text().strip()
        # Generate and persist
        key = secrets.token_urlsafe(32)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.SECRET_FILE.write_text(key)
        return key