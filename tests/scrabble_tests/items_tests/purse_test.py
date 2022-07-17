import pytest
from scrabble_python.errors import EmptyPurse, ScrabbleError
from scrabble_python.helpers import create_distribution
from scrabble_python.items import Purse, Tile


def test_init_purse():
    purse = Purse(lang='fr')
    assert len(purse) == 102
    init_dist = create_distribution('fr', 'dict')
    purse_dist = purse.get_dist()
    for letter in init_dist:
        assert purse_dist[letter] == init_dist[letter]['count']


def test_purse():
    dist = {'A': 1, 'B': 1, 'C': 2}
    purse = Purse(dist, 'fr')
    assert len(purse) == 4
    assert purse.get_dist()['A'] == 1 and purse.get_dist()[
        'B'] == 1 and purse.get_dist()['C'] == 2


def test_draw():
    purse = Purse()
    init_len = len(purse)
    init_dist = purse.get_dist()
    tile = purse.draw()[0]
    assert isinstance(tile, Tile)
    assert purse.get_dist()[tile.letter] == init_dist[tile.letter] - 1
    tiles = purse.draw(5)
    assert isinstance(tiles, list) and isinstance(tiles[0], Tile)
    assert len(tiles) == 5
    assert len(purse) == init_len - 6


def test_empty_purse():
    purse = Purse()
    purse.draw(102)
    with pytest.raises(ScrabbleError) as err_info:
        purse.draw(1)
    assert err_info.typename == EmptyPurse.__name__
    purse = Purse()
    with pytest.raises(ScrabbleError) as err_info:
        purse.draw(103)
    assert err_info.typename == EmptyPurse.__name__
