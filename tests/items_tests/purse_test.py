import pytest
from scrabble_python.items import Purse
from scrabble_python.items import Tile
from scrabble_python.items.helpers import create_distribution
from scrabble_python.errors import ScrabbleError


def test_init_purse():
    purse = Purse(lang='fr')
    assert len(purse) == 102
    init_dist = create_distribution('fr', 'dict')
    purse_dist = purse.get_dist()
    for letter in init_dist:
        assert purse_dist[letter] == init_dist[letter]['count']


def test_purse():
    tiles = [Tile('A'), Tile('B'), Tile('C'), Tile('C')]
    purse = Purse(tiles, 'fr')
    assert len(purse) == 4
    assert purse.get_dist()['A'] == 1 and purse.get_dist()['B'] == 1 and purse.get_dist()['C'] == 2 


def test_draw():
    init_dist = create_distribution('fr', 'dict')
    purse = Purse()
    tile = purse.draw()
    letter = tile.letter
    assert isinstance(tile, Tile)
    assert purse.get_dist()[letter] == init_dist[letter]['count'] - 1
    tiles = purse.draw(5)
    assert isinstance(tiles, list) and isinstance(tiles[0], Tile)


def test_empty_purse():
    purse = Purse()
    purse.draw(102)
    with pytest.raises(ScrabbleError):
        purse.draw(1)
    purse = Purse()
    with pytest.raises(ScrabbleError):
        purse.draw(103)
