from pokecon_extensions.simplifier import Button, Direction, Hat, Press, Print, Sequence, Wait, Match, NotMatchAction, INFINITE

# コマンド名を記述します。
NAME = "簡易自動化のテスト"

# コマンド本体を記述します。
SEQUENCE = Sequence([
    Press(Button.A, 0.1),
    Wait(1),
    Press(Button.B, duration=0.3, wait=1),
    Press(Hat.TOP),

    Sequence([
        Print("hoge"),
        Press(Button.A),
    ], loop=3, not_match=NotMatchAction.Stop),
    
    Press([Button.A, Button.B], duration=2)
])
