from __future__ import annotations

import asyncio
import threading
from contextlib import contextmanager
from typing import Any, Generator

import anyio


class _ThreadPortal:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()
        self._loop.close()
        self._stopped.set()

    def call(self, func, *args):
        return self.start_task_soon(func, *args).result()

    def start_task_soon(self, func, *args, name: Any = None):
        async def runner():
            result = func(*args)
            if asyncio.iscoroutine(result):
                return await result
            return result

        return asyncio.run_coroutine_threadsafe(runner(), self._loop)

    def stop(self, cancel_remaining: bool = False) -> None:
        self._loop.call_soon_threadsafe(self._loop.stop)

    async def sleep_until_stopped(self) -> None:
        while not self._stopped.is_set():
            await asyncio.sleep(0.01)


_SENTINEL = object()


class _AsyncQueue:
    def __init__(self) -> None:
        self.queue: asyncio.Queue | None = None
        self.loop: asyncio.AbstractEventLoop | None = None

    def ensure(self) -> asyncio.Queue:
        if self.queue is None:
            loop = asyncio.get_running_loop()
            self.loop = loop
            self.queue = asyncio.Queue()
        return self.queue


class _ThreadSafeSendStream:
    def __init__(self, q: _AsyncQueue) -> None:
        self._queue = q
        self._closed = False

    async def send(self, item: Any) -> None:
        if self._closed:
            raise anyio.ClosedResourceError
        queue = self._queue.ensure()
        await queue.put(item)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._queue.loop and self._queue.queue:
            asyncio.run_coroutine_threadsafe(self._queue.queue.put(_SENTINEL), self._queue.loop)

    async def aclose(self) -> None:
        self.close()

    @property
    def extra_attributes(self) -> dict:
        return {}


class _ThreadSafeReceiveStream:
    def __init__(self, q: _AsyncQueue) -> None:
        self._queue = q
        self._closed = False

    async def receive(self) -> Any:
        if self._closed:
            raise anyio.ClosedResourceError
        queue = self._queue.ensure()
        item = await queue.get()
        if item is _SENTINEL:
            self._closed = True
            raise anyio.EndOfStream
        return item

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._queue.loop and self._queue.queue:
            asyncio.run_coroutine_threadsafe(self._queue.queue.put(_SENTINEL), self._queue.loop)

    async def aclose(self) -> None:
        self.close()

    @property
    def extra_attributes(self) -> dict:
        return {}


@contextmanager
def start_blocking_portal(*_args, **_kwargs) -> Generator[_ThreadPortal, None, None]:
    portal = _ThreadPortal()
    try:
        yield portal
    finally:
        portal.stop()
        portal._thread.join(timeout=2)


def apply_anyio_portal_patch() -> None:
    try:
        import anyio.from_thread as from_thread
        import anyio.to_thread as to_thread
        import starlette.concurrency as concurrency
    except Exception:
        return

    from_thread.start_blocking_portal = start_blocking_portal
    anyio.create_memory_object_stream = create_memory_object_stream
    to_thread.run_sync = _run_sync
    concurrency.run_in_threadpool = _run_in_threadpool


async def _run_sync(func, *args, cancellable: bool = False, limiter=None):
    del cancellable, limiter
    result = func(*args)
    if asyncio.iscoroutine(result):
        return await result
    return result


async def _run_in_threadpool(func, *args, **kwargs):
    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


def create_memory_object_stream(_max_buffer_size: int = 0):
    q = _AsyncQueue()
    return _ThreadSafeSendStream(q), _ThreadSafeReceiveStream(q)
