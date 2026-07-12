"""
VLESS WebSocket relay — tunneled VLESS connections over WebSocket.
"""

import asyncio
import secrets

from fastapi import WebSocket

from core.shared import (
    LINKS, LINKS_LOCK, stats, hourly_traffic, connections,
    is_link_allowed, now_ir,
)
from modules.rate_limiter import apply_throttle

RELAY_BUF = 262144  # 256 KB


def _client_ip(ws: WebSocket) -> str:
    fwd = ws.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    real = ws.headers.get("x-real-ip", "")
    if real:
        return real.strip()
    return ws.client.host if ws.client else "unknown"


async def _parse_header(chunk: bytes):
    """Parse VLESS protocol header."""
    if len(chunk) < 24:
        raise ValueError("header too short")

    # [version][16-byte UUID][add-on][command][port][addr]
    pos = 1 + 16  # skip version + UUID
    addon_len = chunk[pos]
    pos += 1 + addon_len

    command = chunk[pos]
    pos += 1
    port = int.from_bytes(chunk[pos:pos + 2], "big")
    pos += 2

    addr_type = chunk[pos]
    pos += 1

    if addr_type == 1:  # IPv4
        addr = ".".join(str(b) for b in chunk[pos:pos + 4])
        pos += 4
    elif addr_type == 2:  # Domain
        dlen = chunk[pos]
        pos += 1
        addr = chunk[pos:pos + dlen].decode("utf-8", errors="ignore")
        pos += dlen
    elif addr_type == 3:  # IPv6
        addr = ":".join(f"{(chunk[pos + i] << 8) | chunk[pos + i + 1]:04x}" for i in range(0, 16, 2))
        pos += 16
    else:
        raise ValueError(f"unknown addr type: {addr_type}")

    return command, addr, port, chunk[pos:]


async def _track_traffic(uid: str, nbytes: int):
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link and is_link_allowed(link):
            link["used_bytes"] = link.get("used_bytes", 0) + nbytes
            stats["total_bytes"] += nbytes
            hourly_traffic[now_ir().strftime("%H:00")] += nbytes


async def relay_vless_websocket(websocket: WebSocket, uid: str):
    """Main WebSocket relay handler for VLESS."""
    await websocket.accept()
    ip = _client_ip(websocket)
    conn_id = secrets.token_urlsafe(8)
    connections[uid][conn_id] = {"ip": ip, "connected_at": now_ir().isoformat()}

    try:
        # Read VLESS header
        initial = await websocket.receive_bytes()
        cmd, addr, port, extra = await _parse_header(initial)

        # Validate link
        async with LINKS_LOCK:
            link = LINKS.get(uid)
            if link is None or not is_allowed(link):
                await websocket.close(code=4000, reason="link invalid")
                return

        stats["active_conns"] += 1

        # Connect to target
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(addr, port),
                timeout=10.0,
            )
        except Exception:
            stats["active_conns"] -= 1
            await websocket.close(code=4001, reason="unreachable")
            return

        if extra:
            writer.write(extra)
            await writer.drain()

        async def pump_ws_to_tcp():
            try:
                while True:
                    msg = await websocket.receive()
                    if msg["type"] == "websocket.disconnect":
                        break
                    data = msg.get("bytes", b"")
                    if not data:
                        continue
                    await apply_throttle(uid, len(data))
                    await _track_traffic(uid, len(data))
                    writer.write(data)
                    await writer.drain()
            except Exception:
                pass
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        async def pump_tcp_to_ws():
            try:
                while True:
                    data = await reader.read(RELAY_BUF)
                    if not data:
                        break
                    await apply_throttle(uid, len(data))
                    await _track_traffic(uid, len(data))
                    await websocket.send_bytes(data)
            except Exception:
                pass
            finally:
                try:
                    await websocket.close()
                except Exception:
                    pass

        async with asyncio.TaskGroup() as tg:
            tg.create_task(pump_ws_to_tcp())
            tg.create_task(pump_tcp_to_ws())

    except Exception:
        pass
    finally:
        stats["active_conns"] = max(0, stats["active_conns"] - 1)
        connections.get(uid, {}).pop(conn_id, None)


def is_allowed(link):
    return is_link_allowed(link)