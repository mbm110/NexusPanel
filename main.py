#!/usr/bin/env python3
"""
NexusPanel — Persian Web Management Panel
Entry point for uvicorn.
Railway expects: main:app
"""

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("NexusPanel")

# ── Module-level export for Railway: main:app ───────────────────────────────
# Importing core.app also imports core.router via lifespan,
# which registers all routes before the first request.
from core.app import app, settings

# ── Local development runner ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    PORT = int(os.environ.get("PORT", settings.PORT))
    logger.info(f"NexusPanel starting on port {PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        reload=False,
    )