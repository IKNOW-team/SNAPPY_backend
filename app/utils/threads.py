import anyio
from functools import partial
import asyncio
from typing import Iterable, Awaitable

# ブロッキング I/O をスレッドに逃がす（FastAPIのasyncエンドポイントから呼ぶ用）
async def run_sync(func, *args, **kwargs):
    return await anyio.to_thread.run_sync(partial(func, *args, **kwargs))
  
  
async def bounded_gather(coros: Iterable[Awaitable], limit: int):
    sem = asyncio.Semaphore(limit)
    async def with_sem(coro):
        async with sem:
            return await coro
    return await asyncio.gather(*[with_sem(c) for c in coros], return_exceptions=True)