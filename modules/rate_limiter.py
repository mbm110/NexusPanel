"""
Token Bucket rate limiter — bandwidth throttling per link.
"""

import asyncio
import time

from core.shared import LINKS

_rate_buckets: dict[str, object] = {}
_bucket_locks: dict[str, asyncio.Lock] = {}
_per_uid_lock = asyncio.Lock()
MIN_RATE = 1024  # 1 KB/s floor
MIN_BURST = 16384  # 16 KB burst floor


class TokenBucket:
    __slots__ = ("rate", "capacity", "tokens", "last_refill")

    def __init__(self, rate: int):
        self.rate = max(rate, MIN_RATE)
        self.capacity = max(self.rate, MIN_BURST)
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed > 0:
            self.last_refill = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

    async def consume(self, n: int):
        while True:
            self.refill()
            if self.tokens >= n:
                self.tokens -= n
                return
            deficit = n - self.tokens
            await asyncio.sleep(min(deficit / self.rate, 0.25))


async def apply_throttle(uid: str, nbytes: int):
    """Throttle per-link with per-uid lock (non‑blocking across links)."""
    if nbytes <= 0:
        return
    link = LINKS.get(uid)
    if not link:
        return
    limit = int(link.get("speed_limit_bytes", 0) or 0)
    if limit <= 0:
        return

    # Per-uid bucket + lock so one slow bucket never blocks another
    async with _per_uid_lock:
        if uid not in _bucket_locks:
            _bucket_locks[uid] = asyncio.Lock()
        bucket = _rate_buckets.get(uid)
        if bucket is None or bucket.rate != limit:
            bucket = TokenBucket(limit)
            _rate_buckets[uid] = bucket

    async with _bucket_locks[uid]:
        await bucket.consume(nbytes)


def reset_throttle(uid: str):
    _rate_buckets.pop(uid, None)
    _bucket_locks.pop(uid, None)