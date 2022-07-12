import pytest
from copy import deepcopy
from scrabble_python.errors.scrabble_errors import BoardOverlap, NoCenter, UnalignedTiles
from scrabble_python.items import Board
from scrabble_python.items import Tile
from scrabble_python.items import Word
from scrabble_python.errors import ScrabbleError, BadWords


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


def test_init_board():
    # Empty board
    board = Board()
    assert isinstance(board, Board)
    assert len(board) == 0
    # Valid board
    valid_board = Board(valid_first_tiles)
    assert len(valid_board) == 4
    # Unvalid board, no center
    with pytest.raises(ScrabbleError) as err_info:
        unvalid_board = Board(unvalid_first_tiles)
    assert err_info.typename == NoCenter.__name__


def test_first_add_tiles():
    # First tile must be on center
    board = Board()
    board.add_tiles(valid_first_tiles)
    assert len(board) == 4
    board = Board()
    with pytest.raises(ScrabbleError) as err_info:
        board.add_tiles(unvalid_first_tiles)
    assert err_info.typename == NoCenter.__name__


def test_add_tiles():
    board = Board(valid_first_tiles)
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    board.add_tiles(new_tiles)
    assert len(board) == 6


def test_unaligned_tiles():
    board = Board()
    unaligned_tiles = [Tile('T', (7, 7)), Tile('A', (7, 8)), Tile('E', (6, 7))]
    with pytest.raises(ScrabbleError) as err_info:
        board.add_tiles(unaligned_tiles)
    assert err_info.typename == UnalignedTiles.__name__


def test_overlap_add_tiles():
    board = Board(valid_first_tiles)
    with pytest.raises(ScrabbleError) as err_info:
        overlap_new_tiles = [Tile('T', (7, 7)), Tile(
            'O', (8, 7)), Tile('I', (9, 7))]
        board.add_tiles(overlap_new_tiles)
    assert err_info.typename == BoardOverlap.__name__
    assert err_info.value.overlap_pos == (7, 7)


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
    with pytest.raises(BadWords) as error:
        board.get_new_words(new_tiles)
    assert 'TZW' in (word.text for word in error.value.bad_words)


def test_get_score():
    board = Board()
    score = board.get_score(valid_first_tiles)
    assert score == (1+1+1+1) * 2 # 1+1+1+1 * 2 
    board.add_tiles(valid_first_tiles)
    # score = board.get_score([Tile('E'), Tile('T'), Tile()])
    assert False
