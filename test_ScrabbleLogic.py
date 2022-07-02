from ScrabbleLogic import Board, Purse, Tile, Word
import copy


def test_initial_purse():
    purse = Purse()
    assert isinstance(purse, Purse)
    assert purse.count == 102


def test_purse_draw():
    purse = Purse()
    tile = purse.draw()
    assert isinstance(tile, Tile)
    assert isinstance(tile, dict)
    assert purse.count == 102 - 1


def test_purse_draw_n():
    purse = Purse()
    n = 10
    tiles = purse.draw_n(n)
    assert isinstance(tiles, list)
    assert isinstance(tiles[0], Tile)
    assert purse.count == 102 - n


def test_word():
    word = Word('test')
    assert isinstance(word, Word)


def is_same_values(list, other_list):
    if len(list) != len(other_list):
        return False

    list = [value.upper() for value in list]
    other_list = [value.upper() for value in other_list]

    for value in list:
        if value not in other_list:
            return False
        else:
            other_list.remove(value)
    return True


def test_board():
    maison = Word('maiSon', [3, 4], 'V')
    board = Board(maison)
    assert is_same_values(board.words_on_board(), ['Maison'])
    macon = Word('macon', [3, 4], 'H')
    board.add(macon)
    assert is_same_values(board.words_on_board(), ['Maison', 'MACON'])
    board.add(Tile('H', [4, 5]))
    assert not is_same_values(board.words_on_board(), [
                              'maison', 'macon', 'ah'])
    assert is_same_values(board.words_on_board(), [
                          'maison', 'macon', 'ah', 'ah'])
    # board.add('not_good_thing')
    # assert TypeError raised


def test_compare_words_board():
    maison = Word('maiSon', [3, 4], 'V')
    macon = Word('acon', [3, 5], 'H')
    board = Board(maison)
    board.add(macon)
    old_board = copy.deepcopy(board)
    new_words = board.compare_words(Tile('H', [4, 5]))
    # Check mutations
    assert board == old_board
    # Check new words
    assert is_same_values(new_words, ['ah', 'ah'])
