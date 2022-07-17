import pytest
from scrabble_python import Tile, Word


def test_word_uppercase():
    word = Word('test', (0, 0))
    assert word.text != 'test'
    assert word.text == 'TEST'


def test_word_tile():
    word = Word('test', (0, 0))
    for tile in word.tiles:
        assert isinstance(tile, Tile)


@pytest.mark.parametrize('text,start,direction,pos', [
    ('test', (0, 0), 'H', [(0, 0), (0, 1), (0, 2), (0, 3)]),
    ('tasse', (7, 7), 'V', [(7, 7), (8, 7), (9, 7), (10, 7), (11, 7)]),
])
def test_word_tile_position(text, start, direction, pos):
    word = Word(text, start, direction)
    tiles_pos = [tile.pos for tile in word.tiles]
    assert tiles_pos == pos

@pytest.mark.parametrize('text, score', [('test', 4), ('wagon', 15)])
def test_word_initial_score(text, score):
    word = Word(text, (0, 0))
    assert word.score == score


@pytest.mark.parametrize('text, validity', [('valide', True), ('vallide', False)])
def test_word_validity(text, validity):
    word = Word(text, (2, 5))
    assert bool(word) is validity
