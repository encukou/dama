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


def test_jump_self():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . w w .|
        |. . w . |
    """)
    check_prefix(board, [], {'d2', 'f2'})


def test_jump_opponent():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . w b .|
        |. . w . |
    """)
    check_prefix(board, [], {'e1'})
    check_prefix(board, ['e1'], {'g3'})


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


def test_upgrade():
    board = Board.load("""[w]
        | . . . .|
        |. . w . |
        | . . . .|
        |. . . . |
        | . . . .|
        |b . . . |
        | w . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'b2', 'e7'})
    check_prefix(board, ['e7'], {'d8', 'f8'})
    check_prefix(board, ['e7', 'd8'], {})

    check_move(board, ['e7', 'd8'], """[b]
        | . W . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |b . . . |
        | w . . .|
        |. . . . |
    """)

    check_move(board, ['a3', 'c1'], """[w]
        | . W . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. B . . |
    """)


def test_king():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . W . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'e5'})
    check_prefix(board, ['e5'], {'f6', 'g7', 'h8', 'a1', 'b2', 'c3', 'd4',
                                 'f4', 'g3', 'h2', 'b8', 'c7', 'd6'})


def test_king_take():
    board = Board.load("""[w]
        | . . . .|
        |. . . W |
        | . . . .|
        |. . . . |
        | . . . .|
        |. b . . |
        | . . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'g7'})
    check_prefix(board, ['g7'], {'a1', 'b2'})


def test_king_choice():
    board = Board.load("""[w]
        | . . . .|
        |. . . b |
        | . . . .|
        |. . W . |
        | . . . .|
        |. b . b |
        | . . w .|
        |. . . . |
    """)
    check_prefix(board, [], {'e5'})
    check_prefix(board, ['e5'], {'a1', 'b2', 'h8', 'h2'})


def test_king_lose():
    board = Board.load("""[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . b . .|
        |. b . . |
        | . . . .|
        |W . . . |
    """)
    check_prefix(board, [], {'a1'})
    check_prefix(board, ['a1'], {'b2'})

    check_move(board, ['a1', 'b2'], """[b]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . b . .|
        |. b . . |
        | W . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'c3'})
    check_prefix(board, ['c3'], {'a1'})

    check_move(board, ['c3', 'a1'], """[w]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . b . .|
        |. . . . |
        | . . . .|
        |B . . . |
    """)
    check_prefix(board, [], {})


def test_king_chain():
    board = Board.load("""[w]
        | . . . .|
        |. b . . |
        | . . b .|
        |. . . . |
        | b w . b|
        |. . b . |
        | b . . .|
        |W . . . |
    """)
    check_prefix(board, [], {'a1'})
    check_prefix(board, ['a1'], {'c3'})
    check_prefix(board, ['a1', 'c3'], {'a5'})
    check_prefix(board, ['a1', 'c3', 'a5'], {'d8'})
    check_prefix(board, ['a1', 'c3', 'a5', 'd8'], {'g5'})
    check_prefix(board, ['a1', 'c3', 'a5', 'd8', 'g5'], {'d2', 'c1'})
    check_prefix(board, ['a1', 'c3', 'a5', 'd8', 'g5', 'd2'], {})

    check_move(board, ['a1', 'c3', 'a5', 'd8', 'g5', 'd2'], """[b]
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . w . b|
        |. . . . |
        | . W . .|
        |. . . . |
    """)


def test_king_return():
    board = Board.load("""[w]
        | . . . .|
        |. b b . |
        | W . . .|
        |. b b . |
        | . . . .|
        |. . b . |
        | . . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'b6'})
    check_prefix(board, ['b6'], {'d4', 'd8'})
    check_prefix(board, ['b6', 'd4'], {'f2', 'g1', 'f6', 'g7', 'h8'})
    check_prefix(board, ['b6', 'd4', 'f6'], {'d8'})
    check_prefix(board, ['b6', 'd4', 'f6', 'd8'], {'b6', 'a5'})
    check_prefix(board, ['b6', 'd4', 'f6', 'd8', 'b6'], {})

    check_move(board, ['b6', 'd4', 'f6', 'd8', 'b6'], """[b]
        | . . . .|
        |. . . . |
        | W . . .|
        |. . . . |
        | . . . .|
        |. . b . |
        | . . . .|
        |. . . . |
    """)


def test_promotion_ends_turn():
    board = Board.load("""[w]
        | . . . .|
        |. b b . |
        | w . . .|
        |. . . . |
        | . . . .|
        |. . . . |
        | . . . .|
        |. . . . |
    """)
    check_prefix(board, [], {'b6'})
    check_prefix(board, ['b6'], {'d8'})
    check_prefix(board, ['b6', 'd8'], {})

def test_basic_jump():
    board = Board.load("""[w]
        | b b . .|
        |b . b . |
        | . . . .|
        |. . . w |
        | b . . .|
        |w . . . |
        | . . . .|
        |w . w . |
    """)
    check_prefix(board, [], {'a3'})
    check_prefix(board, ['a3'], {'c5'})
    check_prefix(board, ['a3', 'c5'], {})

