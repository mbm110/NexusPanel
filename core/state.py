"""
Persistent state management.
"""

import json
import os
import aiofiles
from pathlib import Path
from typing import Optional

from core.config import Settings


class StateManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = None

    def _get_lock(self):
        if self._lock is None:
            import asyncio
            self._lock = asyncio.Lock()
        return self._lock

    async def load(self) -> Optional[dict]:
        try:
            self.settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            if self.settings.DATA_FILE.exists():
                async with aiofiles.open(self.settings.DATA_FILE, "r", encoding="utf-8") as f:
                    content = await f.read()
                return json.loads(content)
        except Exception as e:
            import logging
            logging.getLogger("NexusPanel").warning(f"State load failed: {e}")
        return None

    async def save(self, links: dict, subs: dict, auth: dict):
        lock = self._get_lock()
        async with lock:
            try:
                self.settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
                data = {
                    "links": dict(links),
                    "subs": dict(subs),
                    "password_hash": auth.get("password_hash", ""),
                    "saved_at": __import__("datetime").datetime.now().__isoformat__(),
                }
                tmp = self.settings.DATA_FILE.with_suffix(".tmp")
                async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                tmp.replace(self.settings.DATA_FILE)
            except Exception as e:
                import logging
                logging.getLogger("NexusPanel").error(f"State save failed: {e}")