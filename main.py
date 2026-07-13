#!/usr/bin/env python3
"""
NexusPanel — Persian Web Management Panel
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

    # Import app to trigger route setup
    from core.app import app, settings

    PORT = int(os.environ.get("PORT", settings.PORT))
    logger.info(f"NexusPanel starting on port {PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
    )