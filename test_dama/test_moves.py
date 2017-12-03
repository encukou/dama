import pytest

from dama.board import Board
from dama import cli


def check_prefix(board, prefix, expected):
    prefix = [cli.coord_from_name(n) for n in prefix]
    print(board.dump())
    moves = board.possible_moves(prefix)
    got = {cli.coord_name(*m) for m in moves}
    print('->', got)
    assert got == set(expected)
    if expected:
        assert not board.move_finished(prefix)
    else:
        assert board.move_finished(prefix)


def check_move(board, instruction, expected):
    move = [cli.coord_from_name(n) for n in instruction]
    board.make_move(move)
    print(f'After move {"-".join(instruction)}, got:')
    print(board.dump())
    expect_board = Board.load(expected)
    assert board.player == expect_board.player
    assert board.pieces == expect_board.pieces
    assert board == expect_board


def test_initial():
    board = Board()
    check_prefix(board, [], {'a3', 'c3', 'e3', 'g3'})


def test_subsequent():
    board = Board()
    check_prefix(board, ['c3'], {'b4', 'd4'})


def test_ending():
    board = Board()
    check_prefix(board, ['c3', 'd4'], {})


def test_illegal():
    board = Board()
    with pytest.raises(ValueError):
        check_prefix(board, ['a1'], {})


def test_choice():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . b b .|
        |. . w . |
    """)
    check_prefix(board, [], {'e1'})
    check_prefix(board, ['e1'], {'c3', 'g3'})


def test_no_choice():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . b . .|
        |w . w . |
    """)
    check_prefix(board, [], {'e1'})
    check_prefix(board, ['e1'], {'c3'})
    check_prefix(board, ['e1', 'c3'], {})


def test_no_jump_after_move():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. b . . |
        | . . . .|
        |. . w . |
    """)
    check_prefix(board, [], {'e1'})
    check_prefix(board, ['e1'], {'d2', 'f2'})
    check_prefix(board, ['e1', 'd2'], {})


def test_chain():
    board = Board.load("""[w]
        | . b . .|
        |. . b . |
        | . b b .|
        |. b . . |
        | . b . .|
        |. . b . |
        | . b b .|
        |. . w . |
    """)
    check_prefix(board, [], {'e1'})
    check_prefix(board, ['e1'], {'c3', 'g3'})
    check_prefix(board, ['e1', 'c3'], {'e5'})
    check_prefix(board, ['e1', 'c3', 'e5'], {'c7', 'g7'})
    check_prefix(board, ['e1', 'c3', 'e5', 'c7'], {})

    check_move(board, ['e1', 'c3', 'e5', 'c7'], """[b]
        | . b . .|
        |. w b . |
        | . . b .|
        |. b . . |
        | . . . .|
        |. . b . |
        | . . b .|
        |. . . . |
    """)
