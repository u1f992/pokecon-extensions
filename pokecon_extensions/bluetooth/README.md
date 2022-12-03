# BluetoothAdapter

Poke-Controller MODIFIED向けBluetooth自動化

> Windowsでしか動作を確認していませんが、原理としては可能なはずです。*nixへの移植はアカツキさんが取り組んでいることを把握しています。

## Requirements

### [btkeyLib.dll](https://note.com/gamewagashi/n/n4a76066320e9)

ダウンロードして、`bluetooth/btkeyLib/`に配置してください。

### Zadig

ドライバをWinUSBに置き換えます。もろもろ自己責任でお願いします。

ドングルについては、[CSR8510 A10が推奨チップ](https://twitter.com/AT12806379/status/1597938264069263360)です。具体的には[ELECOM LBT-UAN05C2/N](https://www.elecom.co.jp/products/LBT-UAN05C2N.html)で動作を確認しましたが、このドングルであれば必ず成功することを保証するものではありません。

### com0com

導入は[こちら](https://qiita.com/yaju/items/e5818c99857883a59033)の解説を確認してください。

## Usage

PythonコマンドをBluetoothで実行する場合、doメソッドに`bluetooth`デコレーターを付与します。

PokeConのシリアルポートを仮想シリアルポートドライバ（例：[com0com](https://qiita.com/yaju/items/e5818c99857883a59033)）に設定して、対となるポートを`Config`に設定してください。

```python
from __future__ import annotations

from Commands.Keys import Button
from Commands.PythonCommandBase import ImageProcPythonCommand

from pokecon_extensions.bluetooth import bluetooth, Config


class BluetoothTest(ImageProcPythonCommand):

    NAME = "Bluetooth自動化のテスト"
    CONFIG = Config(port="COM6", baudrate=4800, timeout=30)

    def __init__(self, cam):
        super().__init__(cam)

    @bluetooth(CONFIG)
    def do(self):
        self.press(Button.A, 1, 1)
        self.press(Button.A, 1, 1)

```

## Diagram

主軸となる`Adapter`は`Serial`同様`BinaryIO`（`write`メソッドなど）を実装しており、将来的にPokeConに組み込む際に置き換えが簡単になるようにしています。

```mermaid
classDiagram
    class BinaryIO {
        <<interface>>
        +write(data: bytes) int
    }
    class Serial {
    }
    class Adapter {
        -session: Session
    }
    BinaryIO <|-- Serial
    BinaryIO <|-- Adapter
    
    class Session {
        +close()
        +send(data: bytes)
    }

    Session "1"--"0..*" Adapter

    class State {
        +buttons: Button
        +sticks: Sticks
    }
    class Button {
        <<IntFlag>>
    }
    class Sticks {
        +l: Stick | None
        +r: Stick | None
    }
    class Stick {
        +x: int
        +y: int
    }
    State "1"--"1" Button
    State "1"--"1" Sticks
    Sticks "1"--"0..2" Stick

    Session <.. State
```

## Acknowledgments

DLL author: みずようかん ([@AT12806379](https://twitter.com/AT12806379))

Port to *nix: アカツキ ([@pokemium](https://twitter.com/pokemium))
