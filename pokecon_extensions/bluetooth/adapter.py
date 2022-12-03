from __future__ import annotations

from typing import BinaryIO, Iterable, Iterator, List, Optional

from .session import Session


class Adapter(BinaryIO):

    def __init__(self, session: Session) -> None:
        self.__closed = False
        self.__session = session

    def __del__(self):
        self.__closed = True

    @property
    def is_open(self) -> bool:
        return self.__session.is_paired()

    @property
    def mode(self) -> str:
        return ""

    @property
    def name(self) -> str:
        raise NotImplementedError()

    def close(self) -> None:
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
        return True

    def write(self, data: bytes | bytearray) -> int:
        d = data if isinstance(data, bytes) else bytes(data)
        self.__session.send(data)
        return 0

    def writelines(self, lines: Iterable[bytes]) -> None:
        for b in lines:
            self.write(b)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError()

    def __next__(self) -> bytes:
        raise NotImplementedError()
