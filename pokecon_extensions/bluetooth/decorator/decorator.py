from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
import multiprocessing as mp
from pathlib import Path
from time import perf_counter
from typing import Any
from typing_extensions import Literal

from Commands.PythonCommandBase import PythonCommand

from .from_virtual_serial import from_virtual_serial


def bluetooth(config: dict[Literal["port", "baudrate"], Any], timeout: float = 15):
    """
    指定されたメソッドをBluetoothで実行するデコレーター

    ---

    「持ちかた/順番を変える」画面でペアリングを待機してください。

    待機中にキャンセルされた場合、最大待機秒数まで待機したのち、コマンドを停止します。

    Args:
        config (Path): "serial.cfg"
        timeout (float, optional): ペアリングの最大待機秒数。待機秒数内にペアリングされなかった場合も、メソッドは実行されます。
    """
    def _bluetooth(func):
        def _wrapper(*args, **kwargs):

            self: PythonCommand = args[0]

            with mp.Manager() as manager, ProcessPoolExecutor(max_workers=1) as executor:
                cancel = manager.Event()
                is_paired = manager.Event()

                conn = executor.submit(from_virtual_serial,
                                       config, timeout, is_paired, cancel)

                try:
                    start_time = perf_counter()
                    print("wait for pairing...")
                    while not is_paired.is_set() and perf_counter() < start_time + timeout:
                        self.wait(1)
                        self.checkIfAlive()

                    self.wait(1)  # 暴発防止
                    func(*args, **kwargs)

                finally:
                    cancel.set()
                    try:
                        print("shutdown connection...")
                        conn.result()
                    except BrokenProcessPool:
                        # see btkeyLib.py, shutdown
                        print("BrokenProcessPool occured")
        return _wrapper
    return _bluetooth
