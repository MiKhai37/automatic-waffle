from copy import deepcopy

import pytest
from scrabble_python.errors import (BadWords, BoardOverlap, NoCenter,
                                    NoContact, OutOfBoard, ScrabbleError,
                                    UnalignedTiles)
from scrabble_python.items import Board, Tile, Word


def test_init_board():
    # Empty board
    board = Board()
    assert isinstance(board, Board)
    assert len(board) == 0
    # Valid init tiles, with center
    center_tiles = [Tile('T', (7, 7)), Tile('E', (7, 8)),
                    Tile('S', (7, 9)), Tile('T', (7, 10))]
    center_init_board = Board(center_tiles)
    assert len(center_init_board) == 4
    # Unvalid init tiles, no center
    with pytest.raises(ScrabbleError) as err_info:
        no_center_tiles = [Tile('T', (6, 7)), Tile('E', (6, 8)),
                           Tile('S', (6, 9)), Tile('T', (6, 10))]
        Board(no_center_tiles)
    assert err_info.typename == NoCenter.__name__


@pytest.mark.skip(reason="Board initialization already use/test add_tiles method")
def test_first_add_tiles():
    # First tile must be on center
    board = Board()
    center_tiles = [Tile('T', (7, 7)), Tile('E', (7, 8)),
                    Tile('S', (7, 9)), Tile('T', (7, 10))]
    board.add_tiles(center_tiles)
    assert len(board) == 4
    with pytest.raises(ScrabbleError) as err_info:
        no_center_tiles = [Tile('T', (6, 7)), Tile('E', (6, 8)),
                           Tile('S', (6, 9)), Tile('T', (6, 10))]
        Board().add_tiles(no_center_tiles)
    assert err_info.typename == NoCenter.__name__


@pytest.mark.skip(reason="Board initialization already use/test add_tiles method")
def test_add_tiles(test_board: Board):
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    test_board.add_tiles(new_tiles)
    assert len(test_board) == 6


def test_unaligned_tiles():
    board = Board()
    with pytest.raises(ScrabbleError) as err_info:
        unaligned_tiles = [
            Tile('T', (7, 7)), Tile('A', (7, 8)), Tile('E', (6, 7))
        ]
        board.add_tiles(unaligned_tiles)
    assert err_info.typename == UnalignedTiles.__name__


@pytest.mark.parametrize('overlap_tiles, overlap_pos', [
    ([Tile('T', (7, 7)), Tile('O', (8, 7)), Tile('I', (9, 7))], (7, 7)),
    ([Tile('E', (7, 8)), Tile('T', (8, 8))],                    (7, 8)),
    ([Tile('T', (7, 10)), Tile('S', (7, 11))],                  (7, 10))
])
def test_overlap_add_tiles(test_board: Board, overlap_tiles, overlap_pos):
    with pytest.raises(ScrabbleError) as err_info:
        test_board.add_tiles(overlap_tiles)
    assert err_info.typename == BoardOverlap.__name__
    # assert err_info.value.overlap_pos == overlap_pos


def test_off_board_add_tiles(test_board: Board):
    with pytest.raises(ScrabbleError) as err_info:
        off_tiles = [Tile('A', (7, 11)), Tile('M', (7, 12)),
                     Tile('E', (7, 13)), Tile('N', (7, 14)), Tile('T', (7, 15))]
        test_board.add_tiles(off_tiles)
    assert err_info.typename == OutOfBoard.__name__


@pytest.mark.parametrize('no_contact_tiles', [
    [Tile('T', (5, 7)), Tile('E', (5, 8)),
     Tile('S', (5, 9)), Tile('T', (5, 10))],
    [Tile('S', (7, 11)), Tile('S', (7, 13))]
    
])
def test_no_contact_add_tiles(test_board: Board, no_contact_tiles):
    with pytest.raises(ScrabbleError) as err_info:
        test_board.add_tiles(no_contact_tiles)
    assert err_info.typename == NoContact.__name__


def test_remove_tiles(test_board: Board):
    test_board.remove_tiles([Tile('T', (7, 10))])
    assert len(test_board) == 3
    # Error raise if remove unexistant tile
    with pytest.raises(ScrabbleError):
        test_board.remove_tiles([Tile('T', (6, 10))])


def test_get_word(test_board: Board):
    word_on_board = test_board.get_words()
    assert word_on_board == [Word('TEST', (7, 7), 'H')]


def test_no_mutation_after_add_remove_tiles(test_board: Board):
    new_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    old_board = deepcopy(test_board)
    test_board.add_tiles(new_tiles)
    assert test_board != old_board
    test_board.remove_tiles(new_tiles)
    assert test_board == old_board


def test_get_new_words(test_board: Board):
    next_tiles = [Tile('O', (8, 7)), Tile('I', (9, 7))]
    next_words = test_board.get_next_words(next_tiles)
    assert next_words == [Word('TOI', (7, 7), 'V')]
    test_board.add_tiles(next_tiles)
    next_tiles = [Tile('N', (8, 8))]
    next_words = test_board.get_next_words(next_tiles)
    next_word_strs = [word.text for word in next_words]
    assert all(word in next_word_strs for word in ['ON', 'EN'])


def test_get_new_words_unvalid(test_board: Board):
    new_tiles = [Tile('Z', (8, 7)), Tile('W', (9, 7))]
    with pytest.raises(ScrabbleError) as err_info:
        test_board.get_next_words(new_tiles)
    assert err_info.typename == BadWords.__name__
    assert 'TZW' in (word.text for word in err_info.value.bad_words)


@pytest.mark.parametrize('next_tiles, points', [
    ([Tile('T', (7, 7)), Tile('E', (7, 8)), Tile('S', (7, 9)),
      Tile('T', (7, 10))],                                           (1+1+1+1)*2),
    ([Tile('T', (6, 8)), Tile('S', (8, 8)), Tile('T', (9, 8))],    (1*2+1+1*2+1)*1),
    ([Tile('A', (9, 9)), Tile('L', (9, 10)), Tile('E', (9, 11)),
      Tile('N', (9, 12)), Tile('T', (9, 13)), Tile('S', (9, 14))], (1+1*3+1+1+1+1*3+1)*1),
    ([Tile('Y', (6, 14)), Tile('E', (7, 14)), Tile('N', (8, 14))], (10+1+1+1)*3)
])
def test_get_score(empty_test_board: Board, next_tiles, points):
    assert empty_test_board.get_points(next_tiles) == points
    empty_test_board.add_tiles(next_tiles)
