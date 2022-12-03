from ctypes import *
import threading
from time import sleep
from pathlib import Path
import platform


__btkeyLib__ = cdll.LoadLibrary(
    str(Path(__file__).parent.joinpath({
        "Windows": "btkeyLib.dll",
        "Darwin": "btkeyLib.dylib",
        "Linux": "btkeyLib.so",
    }[platform.system()]).resolve()))
__btkeyLib__.send_button.argtypes = (c_uint32, c_uint32)
__btkeyLib__.send_stick_l.argtypes = (c_uint32, c_uint32, c_uint32)
__btkeyLib__.send_stick_r.argtypes = (c_uint32, c_uint32, c_uint32)
__btkeyLib__.send_gyro.argtypes = (c_int16, c_int16, c_int16)
__btkeyLib__.send_accel.argtypes = (c_int16, c_int16, c_int16)
__btkeyLib__.send_padcolor.argtypes = (c_uint32, c_uint32, c_uint32, c_uint32)
__btkeyLib__.gamepad_paired.restype = c_bool


def start(pad_color: int = 0xFFFFFF, button_color: int = 0xFFFFFF, leftgrip_color: int = 0xFFFFFF, rightgrip_color: int = 0xFFFFFF):
    """
    Bluetooth接続を開始するための関数

    引数はコントローラー、ボタン、左グリップ、右グリップの色をカラーコードで指定する
    """
    __btkeyLib__.send_padcolor(
        pad_color, button_color, leftgrip_color, rightgrip_color)
    threading.Thread(target=lambda: __btkeyLib__.start_gamepad()).start()


def is_paired() -> bool:
    """
    Bluetoothでswitchと接続されたかどうかを返す関数(bool)

    switchと接続されるとTrueが返されます
    """
    return __btkeyLib__.gamepad_paired()


def send_button(key: int):
    __btkeyLib__.send_button(key, 0)


def send_stick_l(horizontal: int, vertical: int):
    __btkeyLib__.send_stick_l(horizontal, vertical, 0)


def send_stick_r(horizontal: int, vertical: int):
    __btkeyLib__.send_stick_r(horizontal, vertical, 0)


def shutdown():
    """
    switchとの接続を切る関数

    ---

    # Makeshift solution:

    `btkeyLib.shutdown()`を直接呼ぶと、`concurrent.futures.process.BrokenProcessPool`例外が発生する。呼び出すと、呼び出し元の子プロセスが異常終了する。

    なぜだか不明だが、別スレッドでわずかに待機してから実行すると正常に終了した。デストラクタの呼び出し前にプロセスが後始末されるから？

    """
    def _():
        sleep(0.5)
        __btkeyLib__.shutdown_gamepad()
    threading.Thread(target=_).start()


def gyro(x: int, y: int, z: int):
    """
    実験的機能

    ジャイロの値を設定する関数

    いわゆるジャイロセンサーから取れるデータを設定できる

    dll側では符号付き整数で受け取っているので、符号周りの変換が必要
    """
    __btkeyLib__.send_gyro(x, y, z)


def accel(x: int, y: int, z: int):
    """
    実験的機能

    加速度計の値を設定する関数

    いわゆる加速度センサーから取れるデータを設定できる

    dll側では符号付き整数で受け取っているので、符号周りの変換が必要
    """
    __btkeyLib__.send_accel(x, y, z)
