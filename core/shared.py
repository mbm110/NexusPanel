"""
Shared state module — prevents circular imports.
All global variables live here; other modules import from here.
"""

import asyncio
import hashlib
import secrets
import re
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict, deque
from pathlib import Path

IRAN_TZ = ZoneInfo("Asia/Tehran")

# ── Core state ───────────────────────────────────────────────────────────────
LINKS: dict = {}
SUBS: dict = {}
AUTH = {"password_hash": ""}

stats = {
    "total_bytes": 0,
    "active_conns": 0,
    "created_links": 0,
}
hourly_traffic = defaultdict(int)
connections = defaultdict(dict)
error_logs: deque = deque(maxlen=1000)

LINKS_LOCK = asyncio.Lock()
SUBS_LOCK = asyncio.Lock()

# ── Constants ─────────────────────────────────────────────────────────────────
PROTOCOLS = ["vless-ws", "xhttp-packet-up", "xhttp-stream-up"]
DEFAULT_PROTOCOL = "vless-ws"

FINGERPRINTS = {
    "chrome": {"content-type": "application/grpc", "cache-control": "no-cache, no-store",
               "x-accel-buffering": "no", "server": "cloudflare"},
    "firefox": {"content-type": "application/grpc", "cache-control": "no-cache",
                "x-accel-buffering": "no", "server": "nginx"},
    "safari": {"content-type": "application/grpc", "cache-control": "no-store",
               "x-accel-buffering": "no", "server": "awselb"},
    "ios": {"content-type": "application/grpc", "cache-control": "no-cache, no-transform",
            "x-accel-buffering": "no", "server": "羌中"},
    "android": {"content-type": "application/grpc", "cache-control": "no-cache, no-store",
                "x-accel-buffering": "no", "server": "istio-envoy"},
    "edge": {"content-type": "application/grpc", "cache-control": "no-cache, no-store",
             "x-accel-buffering": "no", "server": "Microsoft-IIS"},
    "360": {"content-type": "application/grpc", "cache-control": "no-cache, no-store",
            "x-accel-buffering": "no", "server": "JDHttp"},
    "qq": {"content-type": "application/grpc", "cache-control": "no-cache, no-store",
           "x-accel-buffering": "no", "server": "tencent"},
}
DEFAULT_FINGERPRINT = "chrome"

DEFAULT_ALPN_BY_PROTOCOL = {
    "vless-ws": ["h2", "http/1.1"],
    "xhttp-packet-up": ["h2"],
    "xhttp-stream-up": ["h2"],
}
DEFAULT_PORT = 443
DEFAULT_SPEED_LIMIT = 0
MIN_PORT, MAX_PORT = 1, 65535

# ── Utility functions ─────────────────────────────────────────────────────────
def now_ir() -> datetime:
    return datetime.now(IRAN_TZ)


def make_password_hash(password: str, secret: str) -> str:
    return hashlib.sha256(f"{secret}{password}".encode()).hexdigest()


def fmt_bytes(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(b) < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def parse_size_to_bytes(value: float, unit: str = "GB") -> int:
    unit = unit.upper()
    multipliers = {"GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}
    return int(value * multipliers.get(unit, 1024**3))


def parse_speed_to_bytes(value: float, unit: str = "MBIT") -> int:
    unit = unit.upper()
    if unit in ("MBIT", "MBPS"):
        return int(value * 1024 * 1024 / 8)
    if unit in ("KBIT", "KBPS"):
        return int(value * 1024 / 8)
    return int(value * 1024 * 1024 / 8)


def make_uuid() -> str:
    return secrets.token_urlsafe(16)


def is_link_allowed(link: dict) -> bool:
    if not link.get("active", True):
        return False
    exp = link.get("expiry_days")
    if exp:
        try:
            created = datetime.fromisoformat(link.get("created_at", datetime.now().isoformat()))
            days = (now_ir() - created.replace(tzinfo=IRAN_TZ)).days
            if days >= int(exp):
                return False
        except Exception:
            pass
    used = link.get("used_bytes", 0)
    total = link.get("total_bytes", 0)
    if total > 0 and used >= total:
        return False
    return True


# ── Link CRUD ─────────────────────────────────────────────────────────────────
def create_link(
    label: str = "", protocol: str = DEFAULT_PROTOCOL,
    fingerprint: str = DEFAULT_FINGERPRINT, alpn: str = "h2",
    port: int = DEFAULT_PORT, total_bytes: int = 0,
    speed_bytes: int = DEFAULT_SPEED_LIMIT, ip_limit: int = 0,
    expiry_days: int = 0, sub_group: str = "",
) -> dict:
    uid = make_uuid()
    link = {
        "id": uid, "label": label, "protocol": protocol,
        "fingerprint": fingerprint, "alpn": alpn, "port": port,
        "total_bytes": total_bytes, "used_bytes": 0,
        "speed_limit_bytes": speed_bytes, "ip_limit": ip_limit,
        "expiry_days": expiry_days, "active": True,
        "created_at": now_ir().isoformat(), "sub_group": sub_group,
    }
    LINKS[uid] = link
    stats["created_links"] += 1
    return link


def remove_link(uid: str) -> bool:
    if uid in LINKS:
        del LINKS[uid]
        return True
    return False


def set_link_active(uid: str, active: bool) -> bool:
    link = LINKS.get(uid)
    if link:
        link["active"] = active
        return True
    return False


# ── Link URL generation ──────────────────────────────────────────────────────
def make_link_url(link: dict, host: str) -> str:
    uid = link["id"]
    fp = link.get("fingerprint", DEFAULT_FINGERPRINT)
    proto = link.get("protocol", "vless-ws")
    port = link.get("port", DEFAULT_PORT)
    label = link.get("label", uid)
    sni = host

    if proto == "vless-ws":
        import urllib.parse
        path = urllib.parse.quote(f"{uid}-wspath")
        return (
            f"vless://{uid}@{host}:{port}"
            f"?encryption=none&fp={fp}&path={path}"
            f"&tls=1&alpn={link.get('alpn','h2')}&sni={sni}&type=ws#—{label}"
        )
    elif "xhttp" in proto:
        import urllib.parse
        path = urllib.parse.quote(f"{uid}-xhpath")
        return (
            f"vless://{uid}@{host}:{port}"
            f"?encryption=none&fp={fp}&sni={sni}&alpn={link.get('alpn','h2')}"
            f"&type=http&path={path}&host={host}&mode=multi#—{label}"
        )
    return f"vless://{uid}@{host}:{port}#—{label}"


# ── Sub groups ────────────────────────────────────────────────────────────────
def create_sub_group(name: str) -> dict:
    gid = make_uuid()
    SUBS[gid] = {"id": gid, "name": name, "link_ids": [], "password": "",
                 "created_at": now_ir().isoformat()}
    return SUBS[gid]


def remove_sub_group(gid: str):
    if gid in SUBS:
        for link in LINKS.values():
            if link.get("sub_group") == gid:
                link["sub_group"] = ""
        del SUBS[gid]


def set_link_sub(uid: str, group_id: str):
    link = LINKS.get(uid)
    if link:
        link["sub_group"] = group_id