
import asyncio
import time
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class RateLimitConfig:
    max_tokens: int = 10  # Maximum burst size (Token Bucket Capacity)
    refill_rate: float = 2.0  # Tokens per second (Refill Rate)
    max_concurrency: int = 5  # Maximum concurrent requests (Semaphore)

class RateLimiter:
    """
    Combines TokenBucket (Rate Limit) and Semaphore (Concurrency Limit).
    Usage:
        async with limiter:
            await make_request()
    """
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.max_tokens)
        self.last_update = time.monotonic()
        self.semaphore = asyncio.Semaphore(config.max_concurrency)
        self._lock = asyncio.Lock()
        
    async def acquire(self):
        """
        Wait until a token is available and semaphore is acquired.
        """
        # 1. Acquire concurrency slot (This limits parallel active requests)
        await self.semaphore.acquire()
        
        # 2. Acquire rate limit token (This limits requests per second)
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self.last_update
                refill = elapsed * self.config.refill_rate
                
                if refill > 0:
                    self.tokens = min(self.config.max_tokens, self.tokens + refill)
                    self.last_update = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return # Successfully acquired token
                
                # Calculate wait time for 1 token
                wait_time = (1.0 - self.tokens) / self.config.refill_rate
            
            # Release lock before sleeping to allow other tasks to check/refill?
            # No, if we release lock, state might change. 
            # But we can't sleep with lock held or no one else can acquire.
            # So we must release lock.
            if wait_time > 0:
                await asyncio.sleep(wait_time)

    def release(self):
        """
        Release concurrency slot.
        """
        try:
            self.semaphore.release()
        except ValueError:
            pass # Ignore if released too many times (shouldn't happen with context manager)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Global limiters
# DeepSeek: 50 requests/sec (example), 10 concurrent
deepseek_limiter = RateLimiter(RateLimitConfig(max_tokens=50, refill_rate=10.0, max_concurrency=10))

# Tavily: 5 requests/sec (example), 5 concurrent
tavily_limiter = RateLimiter(RateLimitConfig(max_tokens=10, refill_rate=2.0, max_concurrency=5))
