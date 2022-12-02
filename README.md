# pokecon-extensions

[Poke-Controller MODIFIED](https://github.com/Moi-poke/Poke-Controller-Modified)向け機能拡張ライブラリ

| 名称                | 機能                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------ |
| `AsynchronousTimer` | 非同期タイマー（待機中に他の操作を挟み込める）を提供します。                                                 |
| `BluetoothAdapter`  | Bluetoothを使用した無線自動化機能を提供します。[README.md](./pokecon_extensions/bluetooth_adapter/README.md) |
| `HeartbeatMonitor`  | `PythonCommand`を監視し、中断された場合に`threading.Event`／`multiprocessing.Event`をセットします。          |
| `Recorder`          | 録画機能を提供します。                                                                                       |
| `simplifier`        | `PythonCommand`の簡易記法を提供します。                                                                      |

## Installation

```sh
pip install git+https://github.com/mukai1011/pokecon-extensions.git@main
```

## Development Guide

開発中にPokeConの内部パッケージを参照するためには、`（Poke-Controller-Modifiedのルート）/SerialController`以下の任意の場所にクローンし、フォルダをeditable modeでインストールしてください。

```sh
# To remove previous installation:
#   pip uninstall pokecon-extensions

cd ./Poke-Controller-Modified/SerialController/where/you/want
git clone https://github.com/mukai1011/pokecon-extensions.git -b develop
pip install -e ./pokecon-extensions
```
