from __future__ import annotations
from enum import Enum, auto
from os import path

from Commands.Keys import Button, Direction, Hat
from Commands.PythonCommandBase import ImageProcPythonCommand, StopThread, TEMPLATE_PATH


INFINITE = -1


class NotMatchAction(Enum):
    Stop = auto()
    """
    `StopThread`を送出し、コマンド実行を停止する
    """
    Break = auto()
    """
    ループから脱出する
    """
    Continue = auto()
    """
    ループを仕切りなおす
    """


class Sequence:
    def __init__(self, sequence: list[Match | Press | Print | Wait | Sequence], loop: int = 1, not_match: NotMatchAction = NotMatchAction.Stop) -> None:
        """
        操作のブロックを表す

        Args:
            sequence (list[Match  |  Press  |  Print  |  Wait  |  Sequence]): 各コマンドオブジェクト|ブロックの配列で操作を記述する
            loop (int, optional): ブロックの繰り返し回数。`INFINITE`を指定すると無限ループ。Defaults to 1.
            not_match (NotMatchAction, optional): 子コマンドオブジェクトの`Match`で、テンプレート画像が見つからなかった場合の挙動。Defaults to NotMatchAction.Stop.

        Raises:
            ValueError: _description_
            TypeError: _description_
        """
        if not isinstance(loop, int) or (loop != INFINITE and loop < 1):
            raise ValueError("loop must be int greater than 1")
        for i, ops in enumerate(sequence):
            if not isinstance(ops, (Match, Press, Print, Wait, Sequence)):
                raise TypeError(f"index:{i} invalid type")

        self.__sequence = sequence
        self.__loop = loop
        self.__not_match = not_match

    def run(self, command: ImageProcPythonCommand):
        i = 0
        flag_break = False
        while (i < self.__loop) if self.__loop != INFINITE else True:
            for j, ops in enumerate(self.__sequence):
                try:
                    ops.run(command)

                except NotMatchError as e:
                    print(f"not match {str(e)}")

                    if self.__not_match == NotMatchAction.Stop:
                        # コマンドの停止
                        # StopThreadを伝播させる
                        raise StopThread()

                    if self.__not_match == NotMatchAction.Break:
                        # Sequenceを脱する
                        # forとwhileをbreakで脱出する
                        print("break")
                        flag_break = True
                        break  # - for

                    else:
                        # Sequenceの周回をやり直す
                        # forから脱出してwhileは継続
                        print("continue")
                        break

                except StopThread:
                    print(f"index:{j} stop command")
                    raise

            i += (1 if self.__loop != INFINITE else 0)
            if flag_break:
                break  # - while


class Print:
    def __init__(self, message: str):
        """
        標準出力に文字列を書き込む（`print`と同等）

        Args:
            message (str): 書き込む文字列
        """
        self.__message = message

    def run(self, command: ImageProcPythonCommand):
        print(self.__message)


class Press:
    def __init__(self, specifier: Button | Direction | Hat | list[Button | Direction | Hat], duration: float = 0.1, wait: float = 0.1) -> None:
        """
        コントローラーを操作する（`self.press()`と同等）

        Args:
            specifier (Button | Direction | Hat | list[Button  |  Direction  |  Hat]): 入力の指定
            duration (float, optional): 入力の継続時間。Defaults to 0.1.
            wait (float, optional): 入力解除後の待機時間。Defaults to 0.1.
        """
        if duration < 0:
            raise ValueError("duration must be greater than 0")
        if wait < 0:
            raise ValueError("wait must be greater than 0")

        self.__specifier = specifier
        self.__duration = duration
        self.__wait = wait

    def run(self, command: ImageProcPythonCommand):
        command.press(self.__specifier, self.__duration, self.__wait)


class Wait:
    def __init__(self, wait: float, fps: float = 1) -> None:
        """
        指定時間待機する（`self.wait()`と同等）

        Args:
            wait (float): 待機時間
            fps (float, optional): waitの単位。原理上デフォルトの1に設定すると、単位は秒になります。Defaults to 1.
        """
        if wait < 0:
            raise ValueError("wait must be greater than 0")
        if fps < 0:
            raise ValueError("fps must be greater than 0")

        self.__wait = wait / fps

    def run(self, command: ImageProcPythonCommand):
        command.wait(self.__wait)


class NotMatchError(Exception):
    pass


class Match:
    def __init__(self, template: str, threshold: float = 0.7, use_gray: bool = True, show_value: bool = False, show_position: bool = True, show_only_true_rect: bool = True, ms: int = 2000, crop=[]):
        """
        現在の画面と指定された画像で、テンプレートマッチングを実行する（`self.isContainTemplate()`と同等）

        - マッチしなかった場合、親の`Sequence`は`NotMatchAction`で指定した処理を行う

        Args:
            template (str): `./Template`起点の相対パス
            threshold (float, optional): マッチ判定の閾値。Defaults to 0.7.
            use_gray (bool, optional): 判定をグレースケール画像で行う。Defaults to True.
            show_value (bool, optional): Defaults to False.
            show_position (bool, optional): Defaults to True.
            show_only_true_rect (bool, optional): Defaults to True.
            ms (int, optional): Defaults to 2000.
            crop (list, optional): Defaults to [].

        Raises:
            FileNotFoundError: _description_
        """
        temp_path = path.join(TEMPLATE_PATH, template)
        if template == "" or not path.exists(temp_path):
            raise FileNotFoundError(temp_path)

        self.__template = template
        self.__threshold = threshold
        self.__use_gray = use_gray
        self.__show_value = show_value
        self.__show_only_true_rect = show_only_true_rect
        self.__ms = ms
        self.__crop = crop

    def run(self, command: ImageProcPythonCommand):
        ret = command.isContainTemplate(self.__template, self.__threshold, self.__use_gray,
                                        self.__show_value, self.__show_only_true_rect, self.__ms, self.__crop)
        if not ret:
            raise NotMatchError(path.join(TEMPLATE_PATH, self.__template))
