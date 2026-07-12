"""
XHTTP Ultra Transport — packet-up and stream-up modes.
"""

import asyncio
import secrets
import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from core.shared import (
    LINKS, LINKS_LOCK, stats, hourly_traffic,
    is_link_allowed, FINGERPRINTS, DEFAULT_FINGERPRINT, now_ir,
)
from modules.rate_limiter import apply_throttle

router = APIRouter()

XHTTP_BUF = 524288
SESSION_TIMEOUT = 30
TCP_TIMEOUT = 10.0
DOWNLINK_Q = 512
SOCK_BUF = 2 * 1024 * 1024


def _headers(fp: str) -> dict:
    return dict(FINGERPRINTS.get(fp, FINGERPRINTS[DEFAULT_FINGERPRINT]))


def _client_ip(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return req.headers.get("x-real-ip", req.client.host if req.client else "unknown")


async def _track(uid: str, nbytes: int):
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link and is_link_allowed(link):
            link["used_bytes"] = link.get("used_bytes", 0) + nbytes
            stats["total_bytes"] += nbytes
            hourly_traffic[now_ir().strftime("%H:00")] += nbytes


async def _drain(reader: asyncio.StreamReader, uid: str):
    """Stream TCP data to caller as async bytes."""
    try:
        while True:
            data = await asyncio.wait_for(reader.read(XHTTP_BUF), timeout=SESSION_TIMEOUT)
            if not data:
                break
            await apply_throttle(uid, len(data))
            await _track(uid, len(data))
            yield data
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass


async def handle_xhttp_request(request: Request, uid: str) -> StreamingResponse:
    """XHTTP packet-up — single request/response."""
    ip = _client_ip(request)

    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link is None or not is_link_allowed(link):
            raise HTTPException(403, "link invalid")

    stats["active_conns"] += 1
    body = await request.body()
    await _track(uid, len(body))

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", 80),
            timeout=TCP_TIMEOUT,
        )
    except Exception:
        stats["active_conns"] -= 1
        raise HTTPException(502, "upstream error")

    writer.write(body)
    await writer.drain()

    fp = link.get("fingerprint", DEFAULT_FINGERPRINT)
    hdrs = _headers(fp)

    async def stream():
        async for chunk in _drain(reader, uid):
            yield chunk
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        stats["active_conns"] = max(0, stats["active_conns"] - 1)

    return StreamingResponse(
        stream(),
        media_type=hdrs.get("content-type", "application/octet-stream"),
        headers={k: v for k, v in hdrs.items() if k != "content-type"},
    )


async def handle_xhttp_stream(request: Request, uid: str) -> StreamingResponse:
    """XHTTP stream-up — persistent connection with adaptive flow control."""
    ip = _client_ip(request)

    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link is None or not is_link_allowed(link):
            raise HTTPException(403, "invalid link")

    stats["active_conns"] += 1

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", 80),
            timeout=TCP_TIMEOUT,
        )
    except Exception:
        stats["active_conns"] -= 1
        raise HTTPException(502, "upstream error")

    down_q: asyncio.Queue = asyncio.Queue(maxsize=DOWNLINK_Q)

    async def uplink():
        try:
            async for chunk in request.stream():
                n = len(chunk)
                await apply_throttle(uid, n)
                await _track(uid, n)
                writer.write(chunk)
                await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def downlink():
        try:
            while True:
                data = await asyncio.wait_for(reader.read(XHTTP_BUF), timeout=SESSION_TIMEOUT)
                if not data:
                    break
                await down_q.put(data)
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

    async def response_stream():
        uplink_task = asyncio.create_task(uplink())
        downlink_task = asyncio.create_task(downlink())

        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(down_q.get(), timeout=1.0)
                    await apply_throttle(uid, len(chunk))
                    yield chunk
                except asyncio.TimeoutError:
                    if uplink_task.done():
                        break
                    continue
        except Exception:
            pass
        finally:
            uplink_task.cancel()
            downlink_task.cancel()
            stats["active_conns"] = max(0, stats["active_conns"] - 1)

    fp = link.get("fingerprint", DEFAULT_FINGERPRINT)
    hdrs = _headers(fp)
    return StreamingResponse(
        response_stream(),
        media_type=hdrs.get("content-type", "application/octet-stream"),
        headers={k: v for k, v in hdrs.items() if k != "content-type"},
    )