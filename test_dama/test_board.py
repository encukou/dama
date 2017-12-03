import textwrap
import pytest

from dama.board import Board


def test_dump():
    board = Board()
    assert board.dump() == textwrap.dedent("""
         [w] abcdefgh
            +--------+
          8 | b b b b| 8
          7 |b b b b | 7
          6 | b b b b| 6
          5 |. . . . | 5
          4 | . . . .| 4
          3 |w w w w | 3
          2 | w w w w| 2
          1 |w w w w | 1
            +--------+
             abcdefgh
    """).lstrip()


def test_initial_player():
    board = Board()
    assert board.player == 'w'


def test_roundtrip():
    situation = textwrap.dedent("""
         [w] abcdefgh
            +--------+
          8 | b b B b| 8
          7 |b w b . | 7
          6 | b b B b| 6
          5 |. . w b | 5
          4 | . B . .| 4
          3 |w B w W | 3
          2 | w w W b| 2
          1 |w B w w | 1
            +--------+
             abcdefgh
    """).lstrip()
    board = Board.load(situation)
    assert board.dump() == situation
