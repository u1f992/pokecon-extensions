from __future__ import annotations

from Commands.Keys import Button
from Commands.PythonCommandBase import ImageProcPythonCommand

from pokecon_extensions.bluetooth import bluetooth, Config


class BluetoothTest(ImageProcPythonCommand):

    NAME = "Bluetooth自動化のテスト"

    def __init__(self, cam):
        super().__init__(cam)

    @bluetooth(Config(port="COM6", baudrate=4800))
    def do(self):
        self.press(Button.A, 1, 1)
        self.press(Button.A, 1, 1)
