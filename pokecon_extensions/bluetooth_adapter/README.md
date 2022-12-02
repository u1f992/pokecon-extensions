# BluetoothAdapter

Poke-Controller MODIFIED向けBluetooth自動化

> 基本的に、`main.py`を見てPythonCommandに組み込める程度の知識を前提としています。
>
> Windowsでしか動作を確認していませんが、原理としては可能なはずです。*nixへの移植はアカツキさんが取り組んでいることを把握しています。

### 準備

DLLは[こちら](https://note.com/gamewagashi/n/n4a76066320e9)からダウンロードして、`./blutooth_adapter/btkeyLib/`に配置してください。

ドングルについては、[CSR8510 A10チップが推奨](https://twitter.com/AT12806379/status/1597938264069263360)です。具体的には[ELECOM LBT-UAN05C2/N](https://www.elecom.co.jp/products/LBT-UAN05C2N.html)で動作を確認しましたが、必ずこのドングルであれば成功することを保証するものではありません。

ドライバは、Zadigを使用してWinUSBに置き換えます。もろもろ自己責任でお願いします。

### 使用方法

`main.py`は仮想シリアルポートを経由してPokeConのシリアル通信出力を受信し、Bluetooth通信に変換するサンプルです。

PokeConのシリアルポートを仮想シリアルポートドライバ（例：[com0com](https://qiita.com/yaju/items/e5818c99857883a59033)）に設定して、`serial.cfg`に対となるポートを設定してください。

実行時は、`main.py`を起動してから、PokeConのPythonコマンドを開始します。先にPythonコマンドを開始していると、シリアル通信が詰まったような挙動になります。

> 暫定的に、`"end"`を受信した際にプログラムが終了するようにしています。空のPythonコマンドを用意して`"end"`だけを送信できるようにしておくと便利です。
> 
> Pythonコマンドに組み込む際は、[aliveプロパティにthreading.Eventオブジェクトを紐づける](https://github.com/mukai1011/pokecon-extensions)などとするのがよいでしょう。

> 主軸となる`BluetoothAdapter`は`Serial`同様`BinaryIO`（`write`メソッドなど）を実装しており、将来的にPokeConに組み込む際に置き換えが簡単になるようにしています。

## Acknowledgments

DLL author: みずようかん ([@AT12806379](https://twitter.com/AT12806379))

Port to *nix: アカツキ ([@pokemium](https://twitter.com/pokemium))
