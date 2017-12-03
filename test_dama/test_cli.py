from dama import cli

import pytest

@pytest.mark.parametrize(['x', 'y', 'name'], [
    (0, 0, 'a1'),
    (1, 0, 'b1'),
    (2, 0, 'c1'),
    (3, 0, 'd1'),
    (4, 0, 'e1'),
    (5, 0, 'f1'),
    (5, 1, 'f2'),
    (5, 2, 'f3'),
    (5, 3, 'f4'),
    (5, 4, 'f5'),
    (5, 5, 'f6'),
    (5, 6, 'f7'),
    (5, 7, 'f8'),
    (6, 7, 'g8'),
    (7, 7, 'h8'),
])
def test_coord_name(x, y, name):
    assert cli.coord_name(x, y) == name
    assert cli.coord_from_name(name) == (x, y)
