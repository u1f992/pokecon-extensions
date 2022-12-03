from __future__ import annotations

from enum import IntEnum, IntFlag, auto
from functools import reduce
from typing import Optional

from pydantic import BaseModel, validator


class Button(IntFlag):
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
    MINIMUM = 0
    NEUTRAL = 0x800
    MAXIMUM = 0xFFF
    # UP = 0xFFF
    # DOWN = 0
    # LEFT = 0
    # RIGHT = 0xFFF


TABLE_BUTTON = {
    0b0000000000000100: Button.Y,
    0b0000000000001000: Button.B,
    0b0000000000010000: Button.A,
    0b0000000000100000: Button.X,
    0b0000000001000000: Button.L,
    0b0000000010000000: Button.R,
    0b0000000100000000: Button.ZL,
    0b0000001000000000: Button.ZR,
    0b0000010000000000: Button.MINUS,
    0b0000100000000000: Button.PLUS,
    0b0001000000000000: Button.LCLICK,
    0b0010000000000000: Button.RCLICK,
    0b0100000000000000: Button.HOME,
    0b1000000000000000: Button.CAPTURE,
}


TABLE_HAT = {
    0: Button.UP,
    1: Button.UP | Button.RIGHT,
    2: Button.RIGHT,
    3: Button.DOWN | Button.RIGHT,
    4: Button.DOWN,
    5: Button.DOWN | Button.LEFT,
    6: Button.LEFT,
    7: Button.UP | Button.LEFT,
    8: Button(0)
}


class Stick(BaseModel):
    x: int
    y: int

    @validator("x")
    def x_axis_must_be_between_0_255(cls, axis: int):
        assert 0x0 <= axis and axis <= 0xff
        return int(axis / 0x100 * 0x1000)

    @validator("y")
    def y_axis_must_be_between_0_255(cls, axis: int):
        assert 0x0 <= axis and axis <= 0xff
        return 0xFFF - int(axis / 0x100 * 0x1000)


class Sticks(BaseModel):
    l: Optional[Stick] = None  # | は不可（3.7だから？）
    r: Optional[Stick] = None


def _from_bytes(data: bytes) -> State:
    line = data.decode("ascii").replace("\r\n", "").split(" ")
    if not (
        line[0] == "end" or
        line[0].startswith("0x")
    ):
        raise ValueError('data must start with "end" or "0x"')

    if line[0] == "end":
        return State()  # ボタンも全部離すけどたぶん大丈夫

    if 6 < len(line) or len(line) < 2:
        raise ValueError(
            "maximum number of elements in data is 6, minimum is 2")

    line.extend(["0"] * (6 - len(line)))  # 要素数が6になるように0でパディング

    try:
        btns, hat, lx, ly, rx, ry = [int(val, 16) for val in line]
    except:
        raise ValueError('elements must be numeric')

    # 含まれるボタンの配列をorでまとめる
    buttons = reduce(lambda a, b: a | b, [
                     t[1] for t in TABLE_BUTTON.items() if btns & t[0]], Button(0)) | TABLE_HAT[hat]
    # btnsの下位2bitで更新を判定する
    sticks = Sticks(l=Stick(x=lx, y=ly) if bool(btns & 0b10) else None,
                    r=Stick(x=rx, y=ry) if bool(btns & 0b01) else None)

    return State(buttons=buttons, sticks=sticks)


class State(BaseModel):
    buttons: Button = Button(0)
    sticks: Sticks = Sticks(
        l=Stick(changed=True, x=128, y=128), r=Stick(changed=True, x=128, y=128))

    @classmethod
    def from_bytes(cls, data: bytes) -> State:
        return _from_bytes(data)
