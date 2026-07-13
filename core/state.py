"""
Persistent state management — async JSON read/write with locking.
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Optional

import aiofiles

from core.config import Settings


class StateManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def load(self) -> Optional[dict]:
        try:
            self.settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            if self.settings.DATA_FILE.exists():
                async with aiofiles.open(self.settings.DATA_FILE, "r", encoding="utf-8") as f:
                    content = await f.read()
                return json.loads(content)
        except Exception:
            pass
        return None

    async def save(self, links: dict, subs: dict, auth: dict):
        lock = self._get_lock()
        async with lock:
            try:
                self.settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

                # Serialize links carefully — convert datetime strings back to strings
                # (they're already strings when created, but guard against raw objects)
                def _serialize_link(lid, link):
                    out = dict(link)
                    for key, val in out.items():
                        if hasattr(val, "isoformat"):
                            out[key] = val.isoformat()
                    return out

                data = {
                    "links": {lid: _serialize_link(lid, link) for lid, link in links.items()},
                    "subs": {gid: dict(sub) for gid, sub in subs.items()},
                    "password_hash": auth.get("password_hash", ""),
                    "saved_at": __import__("datetime").datetime.utcnow().isoformat(),
                }

                tmp = self.settings.DATA_FILE.with_suffix(".tmp")
                async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                tmp.replace(self.settings.DATA_FILE)

            except Exception:
                import logging
                logging.getLogger("NexusPanel").error(
                    "State save failed", exc_info=True
                )