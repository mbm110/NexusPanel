"""
Token Bucket rate limiter — bandwidth throttling per link.
"""

import asyncio
import time

from core.shared import LINKS

_rate_buckets = {}
MIN_RATE = 1024
MIN_BURST = 16384


class TokenBucket:
    __slots__ = ("rate", "capacity", "tokens", "last_refill")

    def __init__(self, rate: int):
        self.rate = max(rate, MIN_RATE)
        self.capacity = max(self.rate, MIN_BURST)
        self.tokens = self.capacity
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
            await asyncio.sleep(min(deficit / self.rate, 0.5))


_bucket_lock = asyncio.Lock()


async def apply_throttle(uid: str, nbytes: int):
    """Throttle if link has speed_limit_bytes > 0."""
    if nbytes <= 0:
        return
    link = LINKS.get(uid)
    if not link:
        return
    limit = int(link.get("speed_limit_bytes", 0) or 0)
    if limit <= 0:
        return
    async with _bucket_lock:
        bucket = _rate_buckets.get(uid)
        if bucket is None or bucket.rate != limit:
            bucket = TokenBucket(limit)
            _rate_buckets[uid] = bucket
    await bucket.consume(nbytes)


def reset_throttle(uid: str):
    _rate_buckets.pop(uid, None)