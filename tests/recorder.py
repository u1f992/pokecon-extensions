from datetime import datetime
from os import path
from threading import Event
from time import perf_counter, sleep

import cv2
import numpy as np

from Commands.PythonCommandBase import ImageProcPythonCommand

from pokecon_extensions import HeartbeatMonitor, Recorder


def current_time(frame: cv2.Mat):
    """現在時刻を表記するフィルター
    """
    cv2.putText(frame, str(datetime.now()), (100, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)
    return frame


def watermark(frame: cv2.Mat):
    """ウォーターマークを付与するフィルター
    """
    mark = np.zeros_like(frame)
    cv2.putText(mark, "sample", (400, 400), cv2.FONT_HERSHEY_SIMPLEX,
                4.0, (255, 255, 255), 5, cv2.LINE_AA)

    frame = cv2.addWeighted(frame, 1, mark, 0.3, 0)
    return frame


class TestRecord(ImageProcPythonCommand):

    NAME = '動画撮影テスト'

    def __init__(self, cam, gui=None):
        super().__init__(cam, gui)

    def do(self):

        # ファイル名は現状mp4のみ対応しています。
        filename = path.join(path.dirname(__file__), "test.mp4")
        print(f"10秒間録画します: {filename}")

        # threading.Eventを、録画停止用のハンドルとして利用します。
        # 録画を停止する際にsetメソッドを呼んでください（スレッドセーフです）。
        handle = Event()
        HeartbeatMonitor(self, handle).start()

        try:
            recorder = Recorder(
                self.camera.camera, self.camera.fps, filename, [current_time, watermark], handle)
        except Exception as e:
            print(str(e))
            return

        recorder.start()

        # self.wait(10)とほぼ同じ意味ですが、GUIのStopに合わせて停止するようにするとこんな感じになります。
        # なお中断されてもファイルは生成されます。
        start_time = perf_counter()
        while perf_counter() < start_time + 10:
            sleep(0.5)
            self.checkIfAlive()

        handle.set()
        recorder.join()

        print(f"録画は正常に終了しました。")
