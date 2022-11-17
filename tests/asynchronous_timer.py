from __future__ import annotations

from datetime import timedelta
from threading import Event
from time import perf_counter

from Commands.Keys import Button
from Commands.PythonCommandBase import ImageProcPythonCommand

from pokecon_extensions import AsynchronousTimer, HeartbeatMonitor


class AccurateAsyncTimer(ImageProcPythonCommand):

    NAME = "正確な非同期タイマーのテスト"

    def __init__(self, cam):
        super().__init__(cam)

    def do(self):

        handle = Event()

        HeartbeatMonitor(self, handle).start()

        wait_time = timedelta(seconds=15)
        calibration = -timedelta(milliseconds=2)  # 較正は各自調整
        timer = AsynchronousTimer(wait_time, calibration, handle)

        start = perf_counter()
        timer.start()  # タイマー開始

        try:
            # ダミーの操作
            for _ in range(5):
                self.press(Button.A, 0.1, 1)

            # 待機時間は後から変更可能
            timer.submit(timedelta(seconds=20))

            timer.join()  # タイマー終了まで待機
            # キャンセルされた場合、joinは即座に正常終了します。
            
            self.checkIfAlive()  # join待機中にGUIから停止されたことを正常に伝達するために、join後は必ずcheckIfAliveを呼びます。

        finally:
            # Eventがセットされているかで、中断されたかを判別できます。
            if handle.is_set():
                print("待機は中断されました。")

        print(perf_counter() - start)
