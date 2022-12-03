from __future__ import annotations

from contextlib import AbstractContextManager
from time import perf_counter, sleep
from types import TracebackType

from pydantic import BaseModel, validator

from .btkeyLib import start, is_paired, send_button, send_stick_l, send_stick_r, shutdown
from .state import State


class ControllerColor(BaseModel):
    pad: int = 0x2D2D2D
    button: int = 0xE6E6E6
    leftgrip: int = 0x464646
    rightgrip: int = 0x464646

    @validator("pad", "button", "leftgrip", "rightgrip")
    def color_code(cls, value: int):
        assert 0x0 <= value and value <= 0xFFFFFF
        return value


class Session(AbstractContextManager):

    #
    # # ContextManagerの呼び出し順確認
    #
    # ## withで使用する場合（推奨）
    #
    # ```
    # with Session() as session:
    #     pass
    # ```
    #
    # 1. __init__
    # 2. __enter__
    # 3. __exit__
    # 4. __del__
    #
    # ## 変数に束縛する場合
    #
    # ```
    # session = Session()
    # # ...
    # session.close()
    # ```
    #
    # 1. __init__
    # 2. close ... たどり着かない可能性がある（例外など）
    # 3. __del__ ... タイミングは指示できないが、必ず呼ばれる
    #

    def __init__(self, controller_color=ControllerColor(), pairing_timeout=30) -> None:
        start(controller_color.pad, controller_color.button,
              controller_color.leftgrip, controller_color.rightgrip)
        start_time = perf_counter()
        while not is_paired() and perf_counter() < start_time + pairing_timeout:
            sleep(1)
        if not is_paired():
            print("pairing timeout")
        self.__closed = False

    def __enter__(self):
        return self

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        self.close()
        return None

    def __del__(self):
        self.close()

    def close(self):
        if self.__closed:
            return
        shutdown()
        self.__closed = True

    def is_paired(self) -> bool:
        return is_paired()

    def send(self, data: bytes):
        state = State.from_bytes(data)
        send_button(state.buttons.value)
        if not state.sticks.l is None:
            send_stick_l(state.sticks.l.x, state.sticks.l.y)
        if not state.sticks.r is None:
            send_stick_r(state.sticks.r.x, state.sticks.r.y)
