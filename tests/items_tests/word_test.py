from scrabble_python.items import Tile
from scrabble_python.items import Word


def test_word_uppercase():
    word = Word('test', (0, 0))
    assert word.text != 'test'
    assert word.text == 'TEST'


def test_word_tile():
    word = Word('test', (0, 0))
    for tile in word.tiles:
        assert isinstance(tile, Tile)


def test_word_tile_position():
    h_word = Word('test', (0, 0))
    v_word = Word('test', (0, 0), 'V')
    h_word_tiles_pos = [tile.pos for tile in h_word.tiles]
    assert h_word_tiles_pos == [(0, 0), (0, 1), (0, 2), (0, 3)]
    v_word_tiles_pos = [tile.pos for tile in v_word.tiles]
    assert v_word_tiles_pos == [(0, 0), (1, 0), (2, 0), (3, 0)]


def test_word_initial_score():
    word4 = Word('test', (0, 0))
    word30 = Word('XYZ', (0, 0))
    assert word4.score == 4
    assert word30.score == 30


def test_word_validity():
    valid_word = Word('valide', (2, 5))
    unvalid_word = Word('vallide', (3, 7))
    assert valid_word
    assert not unvalid_word
