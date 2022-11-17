from __future__ import annotations
from datetime import datetime
from logging import DEBUG, NullHandler, getLogger
import math
from os import makedirs, path
import re
from threading import Event, Thread
from time import perf_counter
from typing import Callable

import cv2
import numpy as np


def _filename_now():
    filename = f"{datetime.now()}.mp4"
    # from https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    s = str(filename).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    return s


class Recorder(Thread):
    """
    画面を録画するスレッド
    """

    def __init__(
        self,
        capture: cv2.VideoCapture,
        fps: int,
        filename: str = path.join("Captures", _filename_now()),
        filters: list[Callable[[cv2.Mat], cv2.Mat]] = [],
        handle: Event = Event()
    ) -> None:
        """
        画面を録画するスレッド

        Args:
            capture (cv2.VideoCapture): 呼び出し元のPythonCommandが保持するVideoCaptureのインスタンス（`self.camera.camera`）
            fps (int): 呼び出し元のPythonCommandが保持するfps（`self.camera.fps`）
            filename (str, optional): 保存ファイル名。省略された場合、`./Captures/`以下に、現在時刻をファイル名として保存します。
            filters (list[Callable[[cv2.Mat], cv2.Mat]], optional): 映像に適用するフィルター。Defaults to `[]`.
            handle (Event, optional): 中断用フラグ。Defaults to `Event()`.
        """
        super().__init__()

        self.__logger = getLogger(__name__)
        self.__logger.addHandler(NullHandler())
        self.__logger.setLevel(DEBUG)
        self.__logger.propagate = True

        if not path.exists(path.dirname(filename)):
            makedirs(path.dirname(filename))

        self.__capture = capture
        if not self.__capture.isOpened():
            raise RuntimeError("capture is not opened")

        # カメラの取得サイズ
        width = int(self.__capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.__capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be a positive integer")

        if fps <= 0:
            raise ValueError("fps must be a positive integer")

        _, ext = path.splitext(filename)
        if ext != ".mp4":
            raise ValueError("currently only mp4 is supported")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # フィルター適用後のサイズ
        mat = np.zeros((height, width, 3), dtype=np.uint8)
        for filter in filters:
            mat = filter(mat.copy())
        height, width, _ = mat.shape
        if width <= 0 or height <= 0:
            raise ValueError(
                "width and height (after filter applied) must be a positive integer")
        size = width, height

        self.__writer_args = filename, fourcc, fps, size
        self.__filters = filters
        self.__handle = handle

    def run(self):

        # 中断の捕捉用
        class OperationCanceledError(Exception):
            pass

        self.__logger.info("Start recording")

        try:
            writer = cv2.VideoWriter(*self.__writer_args)

            fps = self.__writer_args[2]
            interval = 1 / fps
            start_time = perf_counter()  # 開始時刻
            write_count = 0  # 保存したフレーム数
            drop_count = 0  # フレーム落ちした数

            while True:

                if self.__handle.is_set():
                    raise OperationCanceledError()

                if not self.__capture.isOpened():
                    self.__logger.error("Capture is closed")
                    raise OperationCanceledError()
                if not writer.isOpened():
                    self.__logger.error("Writer is closed")
                    raise OperationCanceledError()

                ret, frame = self.__capture.read()
                if not ret:
                    self.__logger.error("Failed to get frame")
                    continue

                # 再生速度補正
                # 参考: https://it-style.jp/?p=766
                estimated_elapsed = write_count * interval
                actual_elapsed = perf_counter() - start_time
                diff = actual_elapsed - estimated_elapsed
                if 0 <= diff:
                    increase = math.ceil(diff / interval)  # 何フレーム書き込むか
                    if 1 < increase:
                        # 取得が遅れている場合
                        # 同じフレーム画像を繰り返し書き込み、辻褄を合わせる。
                        # self.__logger.warning(f"frame dropped! copy {increase - 1} frames to make it up")
                        drop_count += increase - 1
                else:
                    # self.__logger.info(f"get a frame too quickly, no need to write")
                    continue

                for _ in range(increase):

                    _frame = frame.copy()
                    for filter in self.__filters:
                        _frame = filter(_frame.copy())

                    writer.write(_frame)

                write_count += increase

        except:
            pass

        finally:
            writer.release()

            self.__logger.info(
                f"Recording has been stopped by {'handle' if self.__handle.is_set() else 'unknown'}")
            self.__logger.info(f"drop_count: {drop_count}")
