from __future__ import annotations

from threading import Event

from Commands.Keys import Button
from Commands.PythonCommandBase import ImageProcPythonCommand

from pokecon_extensions import HeartbeatMonitor


class TestHeartbeatMonitor(ImageProcPythonCommand):

    NAME = "HeartbeatMonitorクラスのテスト"

    def __init__(self, cam):
        super().__init__(cam)

    def do(self):

        #
        # テストケース
        # いずれの場合も、コマンド自体は「-- finished successfully. --」で停止する。
        #
        # 1. A連打の終了まで待機する。
        # => 「False」と表示される。
        #
        # 2. A連打をはじめたらGUIから停止する
        # => pressがStopThreadを送出しfinallyにかかり、「-- sent a stop request. --」に続いて「True」と表示される。
        #

        obituary = Event()
        HeartbeatMonitor(self, obituary).start()

        try:
            for _ in range(10):
                self.press(Button.A, 0.5, 0.5)
        finally:
            print(obituary.is_set())
