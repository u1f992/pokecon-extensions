from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
import multiprocessing as mp
from time import perf_counter, sleep
from typing_extensions import Protocol

from .config import Config
from .from_virtual_serial import from_virtual_serial


class PythonCommand(Protocol):
    def checkIfAlive(self):
        pass


def bluetooth(config: Config):
    """
    指定されたメソッドをBluetoothで実行するデコレーター

    ---

    「持ちかた/順番を変える」画面でペアリングを待機してください。

    ペアリング待機中にキャンセルされた場合、最大待機秒数まで待機したのち、コマンドを停止します。

    Args:
        config (Config): Configオブジェクト
    """
    def _bluetooth(func):
        def _wrapper(*args, **kwargs):

            self: PythonCommand = args[0]

            with mp.Manager() as manager, ProcessPoolExecutor(max_workers=1) as executor:
                cancel = manager.Event()
                is_paired = manager.Event()

                conn = executor.submit(from_virtual_serial,
                                       config, is_paired, cancel)

                try:
                    start_time = perf_counter()
                    print("wait for pairing...")
                    while not is_paired.is_set() and perf_counter() < start_time + config.timeout:
                        sleep(1)
                        self.checkIfAlive()

                    sleep(1)  # 暴発防止
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
