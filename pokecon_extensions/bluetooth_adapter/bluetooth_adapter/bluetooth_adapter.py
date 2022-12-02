from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from queue import Empty, Queue
import threading as th
from time import perf_counter, sleep
from typing import BinaryIO, Iterable, Iterator, List, Optional

from ..btkeyLib import start, is_paired, holdLfree, holdRfree, shutdown, send_button
from .state import State


def _send(current: State, next: State):

    send_button(next.buttons)

    if not next.sticks.l is None:
        holdLfree(
            next.sticks.l.x, next.sticks.l.y)

    if not next.sticks.r is None:
        holdRfree(
            next.sticks.r.x, next.sticks.r.y)


def _dequeue(queue: Queue[bytes], event: th.Event):

    current = State()

    while not event.is_set():
        try:
            next = State.from_bytes(queue.get(block=False))

        except Empty:
            continue

        except Exception as e:
            print(f"[invalid data]: {str(e)}")
            continue

        _send(current, next)
        current = next

        print(current.dict())


class BluetoothAdapter(BinaryIO):

    def __init__(self, wait_pairing=True) -> None:

        start()
        if wait_pairing:
            print("wait pairing...")
            start_time = perf_counter()
            while not is_paired() and perf_counter() < start_time + 30:
                sleep(0.5)
            if not is_paired():
                print("timeout")

        self.__manager = mp.Manager()
        self.__event = self.__manager.Event()
        self.__queue: Queue[bytes] = self.__manager.Queue()

        self.__executor = ThreadPoolExecutor(max_workers=1)
        self.__thread_dequeue = self.__executor.submit(
            _dequeue, self.__queue, self.__event)

        self.__closed = False

    def __del__(self):
        if not self.closed:
            self.close()

        shutdown()

    @property
    def is_open(self) -> bool:
        return is_paired()

    @property
    def mode(self) -> str:
        return ""

    @property
    def name(self) -> str:
        raise NotImplementedError()

    def close(self) -> None:
        if self.closed:
            return

        try:
            self.__event.set()
            self.__thread_dequeue.result()

        finally:
            self.__executor.shutdown()
            self.__closed = True

    @property
    def closed(self) -> bool:
        return self.__closed

    def fileno(self) -> int:
        raise NotImplementedError()

    def flush(self) -> None:
        raise NotImplementedError()

    def isatty(self) -> bool:
        raise NotImplementedError()

    def read(self, n: int = -1) -> bytes:
        raise NotImplementedError()

    def readable(self) -> bool:
        raise NotImplementedError()

    def readline(self, limit: int = -1) -> bytes:
        raise NotImplementedError()

    def readlines(self, hint: int = -1) -> List[bytes]:
        raise NotImplementedError()

    def seek(self, offset: int, whence: int = 0) -> int:
        raise NotImplementedError()

    def seekable(self) -> bool:
        raise NotImplementedError()

    def tell(self) -> int:
        raise NotImplementedError()

    def truncate(self, size: Optional[int] = None) -> int:
        raise NotImplementedError()

    def writable(self) -> bool:
        return self.__thread_dequeue.running()

    def write(self, data: bytes | bytearray) -> int:
        d = data if isinstance(data, bytes) else bytes(data)
        self.__queue.put(d)
        return 0

    def writelines(self, lines: Iterable[bytes]) -> None:
        for b in lines:
            self.write(b)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.closed:
            self.close()

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError()

    def __next__(self) -> bytes:
        raise NotImplementedError()
