"""
Telegram bot for NexusPanel — management interface.
"""

import asyncio
import os
import logging

import httpx

from core.shared import (
    LINKS, SUBS, create_link, remove_link, set_link_active, make_link_url,
    create_sub_group, remove_sub_group, fmt_bytes, is_link_allowed, now_ir,
)
from core.config import Settings

settings = Settings()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
_admin_raw = os.environ.get("TELEGRAM_ADMIN_IDS", "").strip()
ADMIN_IDS = {int(x) for x in _admin_raw.replace(" ", ",").split(",") if x.isdigit()} if _admin_raw else set()

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
PAGE_SIZE = 6

_client: httpx.AsyncClient | None = None
_running = False
_wizard: dict = {}


async def _client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


async def _send(chat_id: int, text: str, kb: list | None = None) -> dict:
    cl = await _client()
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if kb:
        payload["reply_markup"] = {"inline_keyboard": kb}
    resp = await cl.post(f"{API_BASE}/sendMessage", json=payload)
    return resp.json()


async def _edit(chat_id: int, message_id: int, text: str, kb: list | None = None) -> dict:
    cl = await _client()
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if kb:
        payload["reply_markup"] = {"inline_keyboard": kb}
    resp = await cl.post(f"{API_BASE}/editMessageText", json=payload)
    return resp.json()


async def _answer(call_id: str, text: str = "", alert: bool = False) -> dict:
    cl = await _client()
    payload = {"callback_query_id": call_id, "text": text}
    if alert:
        payload["show_alert"] = True
    resp = await cl.post(f"{API_BASE}/answerCallbackQuery", json=payload)
    return resp.json()


def _kb(*rows):
    return [[{"text": btn, "callback_data": data} for btn, data in row] for row in rows]


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ── Command handlers ──────────────────────────────────────────────────────────
async def cmd_start(chat_id: int):
    text = (
        "🔷 *NexusPanel Bot*\n\n"
        "به ربات مدیریت خوش آمدید!\n\n"
        "/links — لیست لینک‌ها\n"
        "/new — ساخت لینک جدید\n"
        "/groups — گروه‌های ساب\n"
        "/stats — آمار کلی\n"
        "/help — راهنما"
    )
    await _send(chat_id, text, _kb(
        [("🔗 لینک‌ها", "links_0")],
        [("➕ لینک جدید", "new_start")],
        [("📁 گروه‌ها", "groups_0")],
        [("📊 آمار", "stats_show")],
    ))


async def cmd_help(chat_id: int):
    await _send(chat_id,
        "📚 *راهنما*\n\n"
        "/links — لیست لینک‌ها\n"
        "/new — ساخت لینک جدید\n"
        "/groups — گروه‌های ساب\n"
        "/stats — آمار\n"
        "/help — راهنما"
    )


async def cmd_stats(chat_id: int, host: str):
    from core.shared import stats, hourly_traffic
    text = (
        f"📊 *آمار NexusPanel*\n\n"
        f"🔗 لینک‌ها: {len(LINKS)}\n"
        f"📶 ترافیک کل: {fmt_bytes(stats['total_bytes'])}\n"
        f"🔌 اتصال فعال: {stats['active_conns']}\n"
    )
    await _send(chat_id, text)


async def cmd_links(chat_id: int, message_id: int | None, page: int = 0):
    uids = list(LINKS.keys())
    total = len(uids)
    start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, total)

    if not uids:
        await _send(chat_id, "❌ لینکی وجود ندارد. از /new استفاده کنید.")
        return

    text = f"🔗 *لینک‌ها* (صفحه {page + 1}/{max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)})\n\n"
    rows = []
    for uid in uids[start:end]:
        l = LINKS[uid]
        status = "✅" if l.get("active") else "⛔"
        rows.append([(f"{status} {l.get('label') or uid[:8]}", f"detail_{uid}")])

    nav = []
    if page > 0:
        nav.append(("◀️", f"links_{page - 1}"))
    if end < total:
        nav.append(("▶️", f"links_{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([("🔙 منو", "back_main")])

    if message_id:
        await _edit(chat_id, message_id, text, rows)
    else:
        await _send(chat_id, text, rows)


# ── Callback router ────────────────────────────────────────────────────────────
async def handle_callback(call: dict):
    call_id = call["id"]
    chat_id = call["message"]["chat"]["id"]
    user_id = call["from"]["id"]
    data = call["data"]

    if not _is_admin(user_id):
        await _answer(call_id, "❌ دسترسی ندارید", True)
        return

    await _answer(call_id, "")

    if data == "back_main":
        await cmd_start(chat_id)
    elif data == "stats_show":
        await cmd_stats(chat_id, "HOST")
    elif data.startswith("links_"):
        page = int(data.split("_")[1])
        await cmd_links(chat_id, call["message"]["message_id"], page)
    elif data.startswith("detail_"):
        uid = data.replace("detail_", "")
        link = LINKS.get(uid)
        if not link:
            await _answer(call_id, "❌ پیدا نشد", True)
            return
        text = (
            f"🔗 *{link.get('label') or uid[:12]}*\n\n"
            f"پروتکل: `{link.get('protocol', 'vless-ws')}`\n"
            f" Fingerprint: `{link.get('fingerprint', 'chrome')}`\n"
            f" حجم: {fmt_bytes(link.get('used_bytes', 0))} / {fmt_bytes(link.get('total_bytes', 0)) or '∞'}\n"
            f" وضعیت: {'✅ فعال' if link.get('active') else '⛔ غیرفعال'}\n"
        )
        await _edit(chat_id, call["message"]["message_id"], text, _kb(
            [("⏸ تغییر وضعیت", f"toggle_{uid}"), ("🗑 حذف", f"del_{uid}")],
            [("🔙 بازگشت", "links_0")],
        ))
    elif data.startswith("toggle_"):
        uid = data.replace("toggle_", "")
        link = LINKS.get(uid)
        if link:
            link["active"] = not link.get("active", True)
        await cmd_links(chat_id, call["message"]["message_id"], 0)
    elif data.startswith("del_"):
        uid = data.replace("del_", "")
        remove_link(uid)
        await _answer(call_id, "🗑 حذف شد", True)
        await cmd_links(chat_id, call["message"]["message_id"], 0)
    elif data.startswith("groups_"):
        page = int(data.split("_")[1])
        await cmd_groups(chat_id, call["message"]["message_id"], page)
    elif data.startswith("new_start"):
        _wizard[chat_id] = {"step": "label", "data": {}}
        await _edit(chat_id, call["message"]["message_id"],
            "➕ *ساخت لینک*\n\nمرحله ۱ — برچسب (نام) را بفرستید:\nیا 'لغو'",
            _kb([("❌ لغو", "back_main")]))
    elif data == "wizard_cancel":
        _wizard.pop(chat_id, None)
        await cmd_start(chat_id)
    else:
        await _answer(call_id, "در حال توسعه...")


async def cmd_groups(chat_id: int, message_id: int | None, page: int = 0):
    gids = list(SUBS.keys())
    total = len(gids)
    start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, total)

    if not gids:
        await _send(chat_id, "❌ گروهی وجود ندارد.")
        return

    text = f"📁 *گروه‌های ساب* (صفحه {page + 1})\n\n"
    rows = []
    for gid in gids[start:end]:
        g = SUBS[gid]
        rows.append([(f"📁 {g['name']} ({len(g.get('link_ids', []))} لینک)", f"group_{gid}")])

    nav = []
    if page > 0:
        nav.append(("◀️", f"groups_{page - 1}"))
    if end < total:
        nav.append(("▶️", f"groups_{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([("🔙 منو", "back_main")])

    if message_id:
        await _edit(chat_id, message_id, text, rows)
    else:
        await _send(chat_id, text, rows)


# ── Message handler ────────────────────────────────────────────────────────────
async def handle_message(msg: dict):
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = msg.get("text", "")

    if not _is_admin(user_id):
        return

    # Wizard
    if chat_id in _wizard:
        w = _wizard[chat_id]
        step = w["step"]
        if step == "label":
            if text in ("لغو", "cancel"):
                _wizard.pop(chat_id, None)
                await cmd_start(chat_id)
                return
            w["data"]["label"] = text.strip()
            w["step"] = "protocol"
            await _send(chat_id,
                "➕ مرحله ۲ — *پروتکل:*\n\n"
                "1️⃣ WebSocket\n"
                "2️⃣ XHTTP Packet-Up\n"
                "3️⃣ XHTTP Stream-Up",
                _kb([("❌ لغو", "wizard_cancel")]))
        elif step == "protocol":
            m = {"1": "vless-ws", "2": "xhttp-packet-up", "3": "xhttp-stream-up"}.get(text.strip())
            if m:
                w["data"]["protocol"] = m
                w["step"] = "volume"
                await _send(chat_id,
                    "➕ مرحله ۳ — *حجم (GB)*:\n\n"
                    "مثلاً: 10 یا 0 برای نامحدود",
                    _kb([("❌ لغو", "wizard_cancel")]))
            else:
                await _send(chat_id, "❌ گزینه نامعتبر. 1، 2 یا 3 بفرستید.")
        elif step == "volume":
            try:
                vol = float(text.strip()) if text.strip() else 0
                if vol < 0:
                    raise ValueError
                w["data"]["total_gb"] = vol
                w["step"] = "speed"
                await _send(chat_id,
                    "➕ مرحله ۴ — *سرعت (Mbps)*:\n\n"
                    "مثلاً: 10 یا 0 برای نامحدود",
                    _kb([("❌ لغو", "wizard_cancel")]))
            except ValueError:
                await _send(chat_id, "❌ عدد معتبر بفرستید.")
        elif step == "speed":
            try:
                speed = int(text.strip()) if text.strip() else 0
                w["data"]["speed_mbps"] = speed
                w["step"] = "done"
            except ValueError:
                await _send(chat_id, "❌ عدد معتبر بفرستید.")
                return
            # Create link
            from core.shared import parse_size_to_bytes
            d = w["data"]
            link = create_link(
                label=d.get("label", ""),
                protocol=d.get("protocol", "vless-ws"),
                total_bytes=parse_size_to_bytes(d.get("total_gb", 0), "GB"),
                speed_bytes=int(d.get("speed_mbps", 0) * 1024 * 1024 / 8),
            )
            _wizard.pop(chat_id, None)
            await _send(chat_id, f"✅ لینک ساخته شد!\n\n🔗 /links")
        return

    # Commands
    if text.startswith("/start"):
        await cmd_start(chat_id)
    elif text.startswith("/help"):
        await cmd_help(chat_id)
    elif text.startswith("/stats"):
        await cmd_stats(chat_id, "HOST")
    elif text.startswith("/links"):
        await cmd_links(chat_id, None, 0)
    elif text.startswith("/new"):
        _wizard[chat_id] = {"step": "label", "data": {}}
        await _send(chat_id,
            "➕ *ساخت لینک جدید*\n\n"
            "برچسب (نام) لینک را بفرستید:\nیا 'لغو' برای انصراف",
            _kb([("❌ لغو", "wizard_cancel")]))
    elif text.startswith("/groups"):
        await cmd_groups(chat_id, None, 0)


# ── Long polling ──────────────────────────────────────────────────────────────
async def poll(offset: int = 0):
    cl = await _client()
    while _running:
        try:
            resp = await cl.get(
                f"{API_BASE}/getUpdates",
                params={"offset": offset, "timeout": 30, "allowed_updates": ["message", "callback_query"]},
                timeout=35.0,
            )
            data = resp.json()
            if not data.get("ok"):
                await asyncio.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                if "callback_query" in update:
                    await handle_callback(update["callback_query"])
                elif "message" in update:
                    await handle_message(update["message"])

        except Exception as e:
            import logging
            logging.getLogger("NexusPanel.TG").error(f"Poll error: {e}")
            await asyncio.sleep(5)


async def start_bot():
    global _running
    if not BOT_TOKEN or not ADMIN_IDS:
        import logging
        logging.getLogger("NexusPanel.TG").info("Telegram bot: not configured")
        return
    _running = True
    asyncio.create_task(poll())
    import logging
    logging.getLogger("NexusPanel.TG").info(f"Bot started — admins: {ADMIN_IDS}")


async def stop_bot():
    global _running
    _running = False