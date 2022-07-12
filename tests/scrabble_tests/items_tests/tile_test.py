import pytest
from scrabble_python.items import Tile


def test_tile_uppercase():
    tile = Tile('a')
    assert tile.letter == 'A'
    assert tile.letter != 'a'

@pytest.mark.parametrize('letter,value', [('A', 1), ('B', 3), ('Z', 10), ('*', 0)])
def test_tile_value_fr(letter, value):
    tile = Tile(letter)
    assert tile.value == value

def test_tile_eq():
    tile1 = Tile('a')
    tile2 = Tile('A')
    assert tile1 == tile2
    tileB = Tile('B')
    assert tile1 != tileB
    tileA = Tile('A', (1, 1))
    tileAbis = Tile('A', (1, 2))
    assert tileA != tileAbis
    tileAter = Tile('a', (1, 1))
    assert tileA == tileAter
