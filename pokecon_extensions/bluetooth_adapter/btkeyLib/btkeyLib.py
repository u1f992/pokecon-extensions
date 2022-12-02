from ctypes import *
from enum import IntFlag, IntEnum, auto
import threading
import time
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


class Button(IntFlag):
    """
    ボタンのフラグの定義

    Proコンは左右joyconと同じフォーマットでデータを送信しますが、ProコンにSR/SLボタンが無い等の理由で一部のビットは使用できません。
    """
    Y = auto()
    X = auto()
    B = auto()
    A = auto()
    __SR1 = auto()
    __SL1 = auto()
    R = auto()
    ZR = auto()
    MINUS = auto()
    PLUS = auto()
    RCLICK = auto()
    LCLICK = auto()
    HOME = auto()
    CAPTURE = auto()
    __UNUSED = auto()
    __CHARGING = auto()
    DOWN = auto()
    UP = auto()
    RIGHT = auto()
    LEFT = auto()
    __SR2 = auto()
    __SL2 = auto()
    L = auto()
    ZL = auto()


class Direction(IntEnum):
    """
    スティックの値の定義

    上下と左右それぞれ12bitずつ
    """
    UP = 0xFFF
    DOWN = 0
    LEFT = 0
    RIGHT = 0xFFF
    NEUTRAL = 0x800


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


__flg__ = 0


def press(key: Button, wait: int):
    """
    ボタンを一定時間押して離す関数
    """
    global __flg__
    __flg__ |= key.value
    __btkeyLib__.send_button(__flg__, 0)
    time.sleep(wait)
    __flg__ &= ~key.value
    __btkeyLib__.send_button(__flg__, 0)


def hold(key: Button):
    """
    ボタンをホールドする関数
    """
    global __flg__
    __flg__ |= key.value
    __btkeyLib__.send_button(__flg__, 0)


def release(key: Button):
    """
    ホールドしていたボタンを離す関数
    """
    global __flg__
    __flg__ &= ~key.value
    __btkeyLib__.send_button(__flg__, 0)


def send_button(key: Button):
    __btkeyLib__.send_button(key.value, 0)
    print(key)


def moveL(horizontal: Direction, vertical: Direction, wait: int):
    """
    Lスティックを出来合いの値で倒す関数

    引数は横方向、縦方向、時間

    39行目で定義されているDirectionを使用する
    """
    __btkeyLib__.send_stick_l(horizontal.value, vertical.value, 0)
    time.sleep(wait)
    __btkeyLib__.send_stick_l(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def moveLfree(horizontal: int, vertical: int, wait: int):
    """
    Lスティックを自由な値で倒す関数

    引数は横方向、縦方向、時間

    縦横それぞれの値(0から4095)がどの方向を表しているかは39行目で定義されているDirectionを参照
    """
    __btkeyLib__.send_stick_l(horizontal, vertical, 0)
    time.sleep(wait)
    __btkeyLib__.send_stick_l(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def holdL(horizontal: Direction, vertical: Direction):
    """
    Lスティックを出来合いの値でホールドする関数

    引数は横方向、縦方向

    moveLとは違い、ニュートラルに戻さないので滑らかに移動できる
    """
    __btkeyLib__.send_stick_l(horizontal.value, vertical.value, 0)


def holdLfree(horizontal: int, vertical: int):
    """
    Lスティックを自由な値でホールドする関数
    """
    __btkeyLib__.send_stick_l(horizontal, vertical, 0)


def releaseL():
    """
    ホールドしていたLスティックをニュートラルに戻す関数
    """
    __btkeyLib__.send_stick_l(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def moveR(horizontal: Direction, vertical: Direction, wait: int):
    """
    Rスティックを出来合いの値で倒す関数
    """
    __btkeyLib__.send_stick_r(horizontal.value, vertical.value, 0)
    time.sleep(wait)
    __btkeyLib__.send_stick_r(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def moveRfree(horizontal: int, vertical: int, wait: int):
    """
    Rスティックを自由な値で倒す関数
    """
    __btkeyLib__.send_stick_r(horizontal, vertical, 0)
    time.sleep(wait)
    __btkeyLib__.send_stick_r(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def holdR(horizontal: Direction, vertical: Direction):
    """
    Rスティックを出来合いの値でホールドする関数
    """
    __btkeyLib__.send_stick_r(horizontal.value, vertical.value, 0)


def holdRfree(horizontal: int, vertical: int):
    """
    Rスティックを自由な値でホールドする関数
    """
    __btkeyLib__.send_stick_r(horizontal, vertical, 0)


def releaseR():
    """
    ホールドしていたRスティックをニュートラルに戻す関数
    """
    __btkeyLib__.send_stick_r(Direction.NEUTRAL.value,
                              Direction.NEUTRAL.value, 0)


def shutdown():
    """
    switchとの接続を切る関数

    ---

    # Makeshift solution:

    `btkeyLib.shutdown()`を直接呼ぶと、`concurrent.futures.process.BrokenProcessPool`例外が発生する。呼び出すと、呼び出し元の子プロセスが異常終了する。

    なぜだか不明だが、別スレッドでわずかに待機してから実行すると正常に終了した。デストラクタの呼び出し前にプロセスが後始末されるから？

    """
    def _():
        time.sleep(0.5)
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
