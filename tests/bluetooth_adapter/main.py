from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from configparser import ConfigParser
import multiprocessing as mp
from pathlib import Path
import threading as th
from time import sleep
from typing import Any
from typing_extensions import Literal

from serial import Serial

from pokecon_extensions import BluetoothAdapter


def get_serial_config(config: Path = Path(__file__).parent.joinpath("serial.cfg").resolve()) -> dict[Literal["port", "baudrate"], Any]:
    """
    `serial.cfg`から仮想シリアルポートの設定を読み込む
    """
    parser = ConfigParser()
    parser.read(str(config))
    return {
        "port": parser["Serial"]["port"],
        "baudrate": int(parser["Serial"]["baudrate"])
    }


def from_virtual_serial(event: th.Event):
    """
    "end"を受信するまでシリアルポートから読み出し、BluetoothAdapterに引き渡す

    Args:
        event (th.Event): キャンセル用の`threading.Event`オブジェクト
    """

    # シリアルポートはブロックせず、読み出すデータがなければすぐに空文字列を返すようにする。
    # BluetoothAdapterはBinaryIOを実装しており、Serialと同様にwriteできるほか、withで使用できます。
    with Serial(**get_serial_config(), timeout=0) as ser, BluetoothAdapter() as adapter:
        while not event.is_set():

            data = ser.readline()
            if data == b"":
                continue

            adapter.write(data)

            if data.startswith(b"end"):
                break


def main():

    # Managerの生存範囲がEventの生存範囲と一致します。withでなくても、通常の束縛でも問題ありません（GCによって破棄されます）。
    # ProcessPoolExecutorは通常のProcessでも問題ありませんが、エラーの特定が難しくなります。
    with mp.Manager() as manager, ProcessPoolExecutor(max_workers=1) as executor:

        # キャンセル用のthreading.Eventオブジェクトで、複数スレッドで利用されます。
        event = manager.Event()
        worker = executor.submit(from_virtual_serial, event)

        # このデモでは試験的に、"end"を受信するまで仮想シリアルポートから読み出します。
        while worker.running():
            sleep(0.1)

        event.set()
        try:
            worker.result()
        except BrokenProcessPool:
            # see btkeyLib.py, line 218
            print("BrokenProcessPool occured")


if __name__ == "__main__":
    main()
