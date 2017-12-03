import collections
import string

SubMove = collections.namedtuple('SubMove', ['pos', 'take'])

DIRS = {'w': 1, 'b': -1}

class Board:
    def __init__(self, size=8):
        self.size = size
        self.pieces = {}
        self.player = 'w'
        self._move_cache = {}

        self.valid_coords = {(x, y)
                             for x in range(self.size)
                             for y in range(self.size)
                             if (x + y) % 2 == 0
                            }

        for x in range(self.size):
            for y in range(3):
                if (x + y) % 2 == 0:
                    self.pieces[x, y] = 'w'
            for y in range(self.size-3, self.size):
                if (x + y) % 2 == 0:
                    self.pieces[x, y] = 'b'

    def dump(self):
        rows = [[' ' if (x + y) % 2 == 0 else '.'
                 for x in range(self.size)] for y in range(self.size)]
        for (x, y), c in self.pieces.items():
            rows[self.size-1-y][x] = c
        result = []
        result += [f'[{self.player}] {string.ascii_letters[:self.size]}']
        result += [f'   +{"-" * self.size}+']
        result.extend(f'{self.size-i:2} |{"".join(row)}|{self.size-i:2}'
                      for i, row in enumerate(rows))
        result += [f'   +{"-" * self.size}+']
        result += [f'    {string.ascii_letters[:self.size]}']
        result += ['']
        return '\n'.join(result)

    @classmethod
    def load(cls, source):
        rows = [r for r in source.splitlines() if r.count('|') == 2]
        if not rows:
            raise ValueError('no data found')
        self = cls(size=len(rows))
        self.pieces.clear()
        for ym, row in enumerate(rows):
            pre, row, post = row.split('|')
            y = self.size-1-ym
            if len(row) != self.size:
                raise ValueError('bad number of columns')
            for x, c in enumerate(row):
                if (x, y) in self.valid_coords:
                    if c == '.':
                        continue
                    if c not in 'wbWB':
                        raise ValueError('bad symbol: ' + c)
                    self.pieces[x, y] = c
                else:
                    if c != ' ':
                        raise ValueError('symbol on bad tile: ' + c)
        return self

    def _get_submoves(self, prefix):
        result = {}
        if not prefix:
            result = {}
            max_priority = 0
            for (x, y), c in self.pieces.items():
                if c.lower() == self.player:
                    moves = self.get_submoves([(x, y)])
                    for submove in moves.values():
                        if not submove.take:
                            priority = 0
                        elif c.islower():
                            priority = 1
                        else:
                            priority = 2
                        if priority < max_priority:
                            continue
                        elif priority > max_priority:
                            max_priority = priority
                            result.clear()
                        result[x, y] = SubMove((x, y), None)
        else:
            removed = {}
            prev = [prefix[0]]
            jumping = False
            for coord in prefix[1:]:
                try:
                    f = self.get_submoves(prev)[coord]
                except KeyError:
                    raise ValueError('bad prefix')
                if f.take:
                    removed[f.take] = self.pieces[f.take]
                    jumping = True
                else:
                    return {}
                prev += (coord,)
            for x_direction in -1, 1:
                y_direction = DIRS[self.player]
                x, y = prefix[-1]
                x += x_direction
                y += y_direction
                if (x, y) not in self.valid_coords:
                    continue
                p = self.pieces.get((x, y))
                if not p:
                    if jumping:
                        continue
                    result[x, y] = SubMove((x, y), None)
                elif p.lower() != self.player:
                    coord = x + x_direction, y + y_direction
                    if coord not in self.valid_coords or coord in self.pieces:
                        continue
                    if not jumping:
                        result.clear()
                        jumping = True
                    result[coord] = SubMove((coord), (x, y))
        return result

    def get_submoves(self, prefix):
        prefix = tuple(prefix)
        try:
            c = self._move_cache[prefix]
        except KeyError:
            c = self._move_cache[prefix] = self._get_submoves(prefix)
        return c

    def possible_moves(self, prefix):
        if prefix and prefix[0] not in self.get_submoves([]):
            raise ValueError('bad prefix')
        return set(self.get_submoves(prefix))

    def move_finished(self, prefix):
        return not self.possible_moves(prefix)
