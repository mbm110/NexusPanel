"""
NexusProxy — VLESS/XHTTP Gateway
Simplified app.py — uses shared state from core.shared
"""

import os
import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings
from core.state import StateManager
from core.shared import LINKS, SUBS, AUTH, stats, make_password_hash, now_ir

settings = Settings()
state = StateManager(settings)

app = FastAPI(title="NexusProxy", docs_url=None, redoc_url=None)

# ── Startup initialization (sync, runs at import + on each uvicorn start) ─────
def _init_auth():
    """Initialize password hash if not already set."""
    if not AUTH["password_hash"]:
        AUTH["password_hash"] = make_password_hash(settings.DEFAULT_PASSWORD, settings.secret)

_init_auth()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def load_state():
    data = await state.load()
    if data:
        LINKS.update(data.get("links", {}))
        SUBS.update(data.get("subs", {}))
        if "password_hash" in data:
            AUTH["password_hash"] = data["password_hash"]
        import logging
        logging.getLogger("NexusProxy").info(f"Loaded: {len(LINKS)} links, {len(SUBS)} groups")


async def save_state():
    await state.save(LINKS, SUBS, AUTH)


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


def make_link(link: dict, host: str) -> str:
    from core.shared import make_link_url
    return make_link_url(link, host)


# ── Lifespan ──────────────────────────────────────────────────────────────────
async def lifespan(app: FastAPI):
    await load_state()
    if not AUTH["password_hash"]:
        AUTH["password_hash"] = make_password_hash(settings.DEFAULT_PASSWORD, settings.secret)
        await save_state()

    # Setup routes after state is loaded
    from core.router import setup_routes
    setup_routes(app, save_state, get_host)

    yield

    await save_state()


app.router.lifespan_context = lifespan

logger = __import__("logging").getLogger("NexusProxy")