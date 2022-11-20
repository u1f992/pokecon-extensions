from __future__ import annotations
from logging import DEBUG, NullHandler, getLogger

from threading import Event, Thread
from time import sleep
from typing_extensions import Protocol


class PythonCommand(Protocol):
    @property
    def alive(self) -> bool:
        pass


class HeartbeatMonitor(Thread):
    """
    PythonCommandの死活監視を実施するスレッド
    """

    def __init__(self, command: PythonCommand, obituary: Event, interval: float = 1):
        """
        PythonCommandの死活監視を実施するスレッド

        プロパティaliveがFalseになったら、Eventをセットして終了する。

        Args:
            command (PythonCommand): PythonCommand／ImageProcPythonCommand（`self`）
            obituary (Event): PythonCommandの終了時にセットされるEventオブジェクト
            interval (float, optional): PythonCommandの生存を確認する間隔（秒）。Defaults to 1.
        """
        super().__init__()

        self.__logger = getLogger(__name__)
        self.__logger.addHandler(NullHandler())
        self.__logger.setLevel(DEBUG)
        self.__logger.propagate = True

        self.__command = command
        self.__obituary = obituary
        self.__interval = interval

    def run(self):
        self.__logger.info("start monitoring")

        while self.__command.alive:
            sleep(self.__interval)

        self.__logger.info("death detected")
        self.__obituary.set()
