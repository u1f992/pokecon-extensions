from __future__ import annotations

import threading as th

from serial import Serial

from .config import Config
from ..adapter import Adapter
from ..session import Session


def from_virtual_serial(config: Config, is_paired: th.Event, cancel: th.Event):
    """
    （暫定）仮想シリアルポートドライバを経由して、PokeConの通信をBluetoothに引き渡す

    Args:
        config (Path): 設定ファイルのパス
        timeout (int): ペアリングを待機する秒数
        is_paired (th.Event): ペアリング成功を伝達するイベントオブジェクト
        cancel (th.Event): 停止用のイベントオブジェクト
    """
    with Serial(config.port, config.baudrate, timeout=0) as ser, Session(pairing_timeout=config.timeout) as session, Adapter(session) as adapter:
        is_paired.set()
        while not cancel.is_set():

            # シリアルポートはブロックせず、読み出すデータがなければすぐに空文字列を返す。
            data = ser.readline()
            if data == b"":
                continue

            adapter.write(data)
