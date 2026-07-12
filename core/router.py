"""
Main HTTP/WebSocket router and API endpoints.
"""

import os
from fastapi import Request, WebSocket, HTTPException
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse

from core.shared import (
    LINKS, SUBS, AUTH, stats, hourly_traffic, error_logs,
    is_link_allowed, fmt_bytes, make_password_hash, make_uuid,
    create_link, remove_link, set_link_active, make_link_url,
    create_sub_group, remove_sub_group, set_link_sub, now_ir,
)
from core.config import Settings
settings = Settings()

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
}
DEFAULT_FINGERPRINT = "chrome"
DEFAULT_PORT = 443
DEFAULT_PROTOCOL = "vless-ws"


def get_client_ip(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return req.headers.get("x-real-ip", req.client.host if req.client else "unknown")


def verify_password(password: str) -> bool:
    ph = make_password_hash(password, settings.secret)
    return secrets.compare_digest(ph, AUTH["password_hash"])


def get_password_from_cookie(request: Request) -> str:
    return request.cookies.get("nexus_pass", "")


async def api_login(request: Request) -> JSONResponse:
    body = await request.json()
    password = body.get("password", "")
    if verify_password(password):
        resp = JSONResponse({"ok": True})
        resp.set_cookie("nexus_pass", password, httponly=True, samesite="lax", max_age=86400 * 30)
        return resp
    return JSONResponse({"ok": False, "error": "Wrong password"}, status_code=401)


async def api_stats(request: Request) -> JSONResponse:
    return JSONResponse({
        "total_bytes": stats["total_bytes"],
        "active_conns": stats["active_conns"],
        "created_links": stats["created_links"],
        "hourly": dict(hourly_traffic),
    })


async def api_links(request: Request) -> JSONResponse:
    return JSONResponse({
        uid: {**link, "is_allowed": is_link_allowed(link)}
        for uid, link in LINKS.items()
    })


async def api_create_link(request: Request) -> JSONResponse:
    body = await request.json()
    link = create_link(
        label=body.get("label", ""),
        protocol=body.get("protocol", DEFAULT_PROTOCOL),
        fingerprint=body.get("fingerprint", DEFAULT_FINGERPRINT),
        alpn=body.get("alpn", "h2"),
        port=int(body.get("port", DEFAULT_PORT) or DEFAULT_PORT),
        total_bytes=int(body.get("total_bytes", 0) or 0),
        speed_bytes=int(body.get("speed_bytes", 0) or 0),
        ip_limit=int(body.get("ip_limit", 0) or 0),
        expiry_days=int(body.get("expiry_days", 0) or 0),
    )
    host = get_host(request)
    return JSONResponse({
        "link": link,
        "vless": make_link_url(link, host),
    })


async def api_remove_link(uid: str, save_fn) -> JSONResponse:
    remove_link(uid)
    await save_fn()
    return JSONResponse({"ok": True})


async def api_toggle_link(uid: str, save_fn) -> JSONResponse:
    link = LINKS.get(uid)
    if link:
        link["active"] = not link["active"]
        await save_fn()
        return JSONResponse({"ok": True, "active": link["active"]})
    return JSONResponse({"ok": False}, status_code=404)


async def api_subs(request: Request) -> JSONResponse:
    return JSONResponse(dict(SUBS))


async def api_create_sub(request: Request, save_fn) -> JSONResponse:
    body = await request.json()
    group = create_sub_group(body.get("name", "Unnamed"))
    await save_fn()
    return JSONResponse({"group": group})


async def api_remove_sub(gid: str, save_fn) -> JSONResponse:
    remove_sub_group(gid)
    await save_fn()
    return JSONResponse({"ok": True})


async def api_logs(request: Request) -> JSONResponse:
    return JSONResponse({"logs": list(error_logs)[-50:]})


def get_host(req: Request) -> str:
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
    if domain:
        return f"https://{domain}"
    host = req.headers.get("host", "")
    if host:
        return f"https://{host}"
    return f"{req.url.scheme}://{req.client.host}"


def setup_routes(app, save_fn, host_fn=None):
    """Register all routes on the FastAPI app."""

    if host_fn is None:
        host_fn = get_host

    from web.pages import LOGIN_HTML, DASHBOARD_HTML

    @app.get("/")
    async def root(request: Request) -> HTMLResponse:
        return HTMLResponse(LOGIN_HTML)

    @app.get("/dashboard")
    async def dashboard(request: Request) -> HTMLResponse:
        if not verify_password(get_password_from_cookie(request)):
            return RedirectResponse("/", status_code=302)
        return HTMLResponse(DASHBOARD_HTML)

    @app.post("/api/login")
    async def login(request: Request):
        return await api_login(request)

    @app.get("/api/stats")
    async def stats_endpoint(request: Request):
        return await api_stats(request)

    @app.get("/api/links")
    async def links_endpoint(request: Request):
        return await api_links(request)

    @app.post("/api/links")
    async def create_link_endpoint(request: Request):
        result = await api_create_link(request)
        await save_fn()
        return result

    @app.delete("/api/links/{uid}")
    async def remove_link_endpoint(uid: str, request: Request):
        return await api_remove_link(uid, save_fn)

    @app.post("/api/links/{uid}/toggle")
    async def toggle_link_endpoint(uid: str, request: Request):
        return await api_toggle_link(uid, save_fn)

    @app.get("/api/subs")
    async def subs_endpoint(request: Request):
        return await api_subs(request)

    @app.post("/api/subs")
    async def create_sub_endpoint(request: Request):
        return await api_create_sub(request, save_fn)

    @app.delete("/api/subs/{gid}")
    async def remove_sub_endpoint(gid: str, request: Request):
        return await api_remove_sub(gid, save_fn)

    @app.get("/api/logs")
    async def logs_endpoint(request: Request):
        return await api_logs(request)

    @app.get("/sub/{gid}")
    async def sub_download(gid: str, request: Request):
        group = SUBS.get(gid)
        if not group:
            raise HTTPException(404, "Not found")
        host = host_fn(request)
        lines = [make_link_url(LINKS[lid], host)
                 for lid in group.get("link_ids", []) if lid in LINKS and is_link_allowed(LINKS[lid])]
        return Response(
            content="\n".join(lines),
            media_type="text/plain",
            headers={"content-disposition": f'attachment; filename="{group["name"]}.txt"'}
        )

    @app.get("/link/{uid}")
    async def get_link_vless(uid: str, request: Request):
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(404)
        host = host_fn(request)
        return Response(make_link_url(link, host), media_type="text/plain")

    @app.websocket("/ws/{uid}")
    async def ws_relay(websocket: WebSocket, uid: str):
        from modules.vless_ws import relay_vless_websocket
        await relay_vless_websocket(websocket, uid)

    # XHTTP routes
    @app.post("/xhttp/{uid}")
    async def xhttp_post(uid: str, request: Request):
        from modules.xhttp_transport import handle_xhttp_request
        return await handle_xhttp_request(request, uid)

    @app.get("/xhttp/{uid}")
    async def xhttp_get(uid: str, request: Request):
        from modules.xhttp_transport import handle_xhttp_stream
        return await handle_xhttp_stream(request, uid)


import secrets