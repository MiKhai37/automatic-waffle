import pytest
from copy import deepcopy
from scrabble_python.items import Board
from scrabble_python.items import Tile
from scrabble_python.items import Word
from scrabble_python.errors import ScrabbleError


valid_first_tiles = [
    Tile('T', (7, 7)),
    Tile('E', (7, 8)),
    Tile('S', (7, 9)),
    Tile('T', (7, 10)),
]

unvalid_first_tiles = [
    Tile('T', (6, 7)),
    Tile('E', (6, 8)),
    Tile('S', (6, 9)),
    Tile('T', (6, 10)),
]


def test_init_empty_board():
    board = Board()
    assert isinstance(board, Board)
    assert len(board) == 0


def test_valid_init_board():
    board = Board(valid_first_tiles)
    assert len(board) == 4


def test_unvalid_init_board():
    with pytest.raises(ScrabbleError):
        board = Board(unvalid_first_tiles)


def test_add_tiles():
    board = Board(valid_first_tiles)
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    board.add_tiles(new_tiles)
    assert len(board) == 6
    # First tile must be on center
    board = Board()
    board.add_tiles(valid_first_tiles)
    assert len(board) == 4
    board = Board()
    with pytest.raises(ScrabbleError):
        board.add_tiles(unvalid_first_tiles)
    assert len(board) == 0


def test_overlap_add_tiles():
    board = Board(valid_first_tiles)
    with pytest.raises(ScrabbleError):
        overlap_new_tiles = [Tile('T', (7, 7)), Tile(
            'O', (8, 7)), Tile('I', (9, 7))]
        board.add_tiles(overlap_new_tiles)
    assert len(board) == 4


def test_remove_tiles():
    board = Board(valid_first_tiles)
    board.remove_tiles([Tile('T', (7, 10))])
    assert len(board) == 3
    # Error raise if remove unexistant tile
    with pytest.raises(ScrabbleError):
        board.remove_tiles([Tile('T', (6, 10))])
    assert len(board) == 3


def test_get_word():
    board = Board(valid_first_tiles)
    word_on_board = board.get_words()
    assert word_on_board == [Word('TEST', (7, 7), 'H')]


def test_eq_after_add_remove_tiles():
    test_board = Board(valid_first_tiles)
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    old_board = deepcopy(test_board)
    test_board.add_tiles(new_tiles)
    test_board.remove_tiles(new_tiles)
    assert test_board == old_board


def test_get_new_words():
    board = Board(valid_first_tiles)
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    old_board = deepcopy(board)
    new_words = board.get_new_words(new_tiles)
    # Mutation check
    assert board == old_board
    assert new_words == [Word('TOI', (7, 7), 'V')]


def test_get_new_words_unvalid():
    board = Board(valid_first_tiles)
    new_tiles = [Tile('Z', (8, 7)), Tile('W', (9, 7))]
    with pytest.raises(ScrabbleError) as error:
        board.get_new_words(new_tiles)
    print(error.value)
    assert 'TZW' in  str(error.value)
        

def test_get_score():
    board = Board()
    score = board.get_score(valid_first_tiles)
    assert score == 4 * 2
    board.add_tiles(valid_first_tiles)
    # score = board.get_score([Tile('E'), Tile('T'), Tile()])

