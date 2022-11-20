from __future__ import annotations

from datetime import timedelta
from logging import DEBUG, NullHandler, getLogger
from threading import Event, Thread
from time import perf_counter, sleep


class AsynchronousTimer(Thread):
    """
    非同期タイマーを実行するスレッド
    """

    def __init__(self, wait_time: timedelta = timedelta(days=365), calibration: timedelta = timedelta(), handle: Event = Event()):
        """
        非同期タイマーを実行するスレッド

        - ミリ秒単位の精度で待機できる
        - 描画／操作スレッドへの負荷を最小限にする
        - 中断できる
        - 開始後に待機時間を変更できる（`submit`）

        Args:
            wait_time (timedelta, optional): 待機時間。Defaults to `timedelta(days=365)`.
            calibration (timedelta, optional): 較正。Defaults to `timedelta()`.
            handle (Event, optional): 中断用フラグ。Defaults to `Event()`.
        """
        super().__init__()

        self.__logger = getLogger(__name__)
        self.__logger.addHandler(NullHandler())
        self.__logger.setLevel(DEBUG)
        self.__logger.propagate = True

        self.__wait_time = wait_time
        self.__calibration = calibration
        self.__handle = handle

        self.__accept_submission = True

    def run(self):

        # 中断の捕捉用
        class OperationCanceledError(Exception):
            pass

        self.__accept_submission = True

        target = self.__wait_time
        left = (target + self.__calibration).total_seconds()

        start_time = perf_counter()
        lap_start = start_time

        try:
            # 残り1秒台になるまでは0.5秒おきにキャンセル可能にしておく
            while 2 < left:
                sleep(0.5)

                if self.__handle.is_set():
                    raise OperationCanceledError()

                if self.__wait_time != target:
                    target = self.__wait_time
                    left = (
                        target + self.__calibration).total_seconds() - (perf_counter() - start_time)
                    self.__logger.info(
                        f"Submission has been accepted: {target}")
                else:
                    left -= (perf_counter() - lap_start)

                lap_start = perf_counter()

            # 端数をビジーウェイトで待機する（wait_time変更不可）
            self.__accept_submission = False
            self.__logger.info(
                "Timer will expire within 2 seconds, you cannot submit after now.")

            left -= (perf_counter() - lap_start)
            start_time = perf_counter()

            while perf_counter() < start_time + left:
                if self.__handle.is_set():
                    raise OperationCanceledError()

            self.__logger.info("Timer completed gracefully.")

        except:
            self.__logger.info(
                f"Timer has been canceled by {'handle' if self.__handle.is_set() else 'unknown'}.")

    def submit(self, wait_time: timedelta):
        """
        待機時間を変更する

        2秒以内にタイマーが終了する場合、変更できない仕様です。

        Args:
            wait_time (timedelta): 変更する待機時間
        """
        if self.__accept_submission:
            self.__wait_time = wait_time
            self.__logger.info(f"Submit: {self.__wait_time}")
        else:
            self.__logger.warning(
                f"Timer will expire shortly, not accept submission.")
