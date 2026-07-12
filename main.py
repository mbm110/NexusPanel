#!/usr/bin/env python3
"""
NexusPanel — VLESS/XHTTP Gateway
Entry point for uvicorn.
"""

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger("NexusPanel")

if __name__ == "__main__":
    import uvicorn
    from core.config import Settings
    settings = Settings()

    # Import app to trigger route setup
    from core.app import app

    logger.info(f"NexusPanel starting on port {settings.PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info",
    )