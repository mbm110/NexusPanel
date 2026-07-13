"""
NexusPanel — Persian Web Management Panel
Simplified app.py — uses shared state from core.shared
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings
from core.state import StateManager
from core.shared import LINKS, SUBS, AUTH, make_password_hash, now_ir

settings = Settings()
state = StateManager(settings)


def _init_auth():
    """Initialize password hash if not already set."""
    if not AUTH["password_hash"]:
        AUTH["password_hash"] = make_password_hash(settings.DEFAULT_PASSWORD, settings.secret)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — load state, register routes, save on shutdown."""
    # Load persisted state
    data = await state.load()
    if data:
        LINKS.update(data.get("links", {}))
        SUBS.update(data.get("subs", {}))
        if "password_hash" in data:
            AUTH["password_hash"] = data["password_hash"]

    # Ensure auth is set
    if not AUTH["password_hash"]:
        AUTH["password_hash"] = make_password_hash(settings.DEFAULT_PASSWORD, settings.secret)

    # Register routes after state is loaded
    from core.router import setup_routes

    async def save_state_and_log():
        await state.save(LINKS, SUBS, AUTH)
        import logging
        logging.getLogger("NexusPanel").info(
            f"Saved: {len(LINKS)} links, {len(SUBS)} groups"
        )

    def get_host(req=None) -> str:
        if req is None:
            domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
            if domain:
                return f"https://{domain}"
            return "https://localhost"
        host = req.headers.get("host", "")
        if host:
            return f"https://{host}"
        return f"{req.url.scheme}://{req.client.host}"

    setup_routes(app, save_state_and_log, get_host)

    yield  # app is running

    # Shutdown — persist state
    await state.save(LINKS, SUBS, AUTH)


# App instance — lifespan registered here so Railway always sees it
app = FastAPI(
    title="NexusPanel",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth on module load (for TestClient)
_init_auth()