import string

from dama.board import Board

PLAYER_NAMES = {'w': 'Bílý', 'b': 'Černý'}


def coord_name(x, y):
    assert x >= 0 and y >= 0
    return string.ascii_lowercase[x] + string.digits[y+1]


def coord_from_name(name):
    col = name[0]
    row = name[1:]
    return string.ascii_lowercase.index(col), int(row) - 1


def run():
    board = Board()
    while True:
        print(board.dump())
        prefix = []
        while True:
            name = PLAYER_NAMES[board.player]
            allowed_submoves = board.get_submoves(prefix)
            answers = {coord_name(*m): m for m in allowed_submoves}
            if not answers:
                break
            if not prefix:
                question = 'odkud hraješ'
            else:
                question = 'kam hraješ'
            while True:
                answer = input(f'{name}, {question} ({", ".join(answers)})? ')
                if not answer:
                    answer = list(answers)[0]
                if answer in answers:
                    break
                print('Nerozumím')
            prefix.append(coord_from_name(answer))
            print('-'.join(coord_name(*m) for m in prefix), end='')
            if board.move_finished(prefix):
                print()
                print()
                break
            print('-')

        if prefix:
            board.make_move(prefix)
        else:
            print(f'{name} nemá žádné další tahy')
            break
