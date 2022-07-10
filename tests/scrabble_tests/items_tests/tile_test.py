from scrabble_python.items import Tile


def test_tile_uppercase():
    tile = Tile('a')
    assert tile.letter == 'A'
    assert tile.letter != 'a'


def test_tile_value_fr():
    tileA = Tile('A')
    tileB = Tile('B')
    tileZ = Tile('Z')
    tileJoker = Tile('*')
    assert tileA.value == 1
    assert tileB.value == 3
    assert tileZ.value == 10
    assert tileJoker.value == 0

def test_tile_equality():
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
