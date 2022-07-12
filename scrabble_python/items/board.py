from pprint import pformat

from scrabble_python.errors import (BadWords, BoardOverlap, NoCenter,
                                    ScrabbleError, UnalignedTiles)

from .tile import Tile
from .word import Word

multipliers = {
    'word_triple': [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)],
    'word_double': [(1, 1), (1, 13), (2, 2), (2, 12), (3, 3), (3, 11), (4, 4), (4, 10), (7, 7), (10, 4), (10, 10), (11, 3), (11, 11), (12, 2), (12, 12), (13, 1), (13, 13)],
    'letter_triple': [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)],
    'letter_double': [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]
}

letter_multipliers = {
    3: [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)],
    2: [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]
}

word_multipliers = {
    3: [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)],
    2: [(1, 1), (1, 13), (2, 2), (2, 12), (3, 3), (3, 11), (4, 4), (4, 10), (7, 7), (10, 4), (10, 10), (11, 3), (11, 11), (12, 2), (12, 12), (13, 1), (13, 13)],
}


class Board:
    def __init__(self, tiles: list[Tile] = None, size: int = 15) -> None:
        self.size = size
        self.center = self.size // 2
        if tiles is None:
            self.tiles = []
        else:
            tiles_pos = [tile.pos for tile in tiles]
            if (self.center, self.center) not in tiles_pos:
                raise NoCenter
            self.tiles = tiles.copy()

    def __str__(self):
        board = self.__format_board()
        return pformat(board)

    def __len__(self):
        return len(self.tiles)

    def __eq__(self, other):
        return isinstance(other, Board)

    def __format_board(self):
        """
        Create and return a list representation of the board
        """
        row = [' '] * self.size
        board = [row.copy() for _ in range(self.size)]
        for tile in self.tiles:
            board[tile.x][tile.y] = tile.letter
        return board

    def add_tiles(self, tiles_to_add: list[Tile]):
        coords_on_board = [tile.pos for tile in self.tiles]
        coords_to_add = [tile.pos for tile in tiles_to_add]
        xs_to_add = [coord[0] for coord in coords_to_add]
        ys_to_add = [coord[1] for coord in coords_to_add]
        # First tile must be on center check
        if len(self) == 0 and (self.center, self.center) not in coords_to_add:
            raise NoCenter
        # Tiles must not overlap
        for coord_to_add in coords_to_add:
            if coord_to_add in coords_on_board:
                raise BoardOverlap(overlap_coord=coord_to_add)
        # Tiles must be on same line
        if max(xs_to_add) - min(xs_to_add) != 0 and max(ys_to_add) - min(ys_to_add) != 0 :
            raise UnalignedTiles
        self.tiles.extend(tiles_to_add)

    def remove_tiles(self, tiles_to_remove: list[Tile]):
        for tile in tiles_to_remove:
            if tile not in self.tiles:
                raise ScrabbleError('tile not in board tiles')
            self.tiles.remove(tile)

    def __get_word_start(self, row_or_col: list[str]):
        """
        Return the start postion of words on a row or a column
        """
        row_or_col = [' '] + row_or_col
        return [i for i, [prev, curr] in enumerate(zip(row_or_col, row_or_col[1:]))
                if prev == ' ' and curr != ' ']

    def get_words_on_board(self) -> list[Word]:
        """
        Returns list[Word] corresponding to the words present on the board in 
        """
        rows = self.__format_board()
        cols = [[row[i] for row in rows] for i in range(len(rows[0]))]
        words = []
        for x, row in enumerate(rows):
            row_word = ''.join(row).split()
            row_index = self.__get_word_start(row)
            row_coords = [*zip([x]*len(row_index), row_index)]
            words.append([*zip(row_word, row_coords, ['H']*len(row_word))])
        for y, col in enumerate(cols):
            col_word = ''.join(col).split()
            col_index = self.__get_word_start(col)
            col_coords = [*zip(col_index, [y]*len(col_index))]
            words.append([*zip(col_word, col_coords, ['V']*len(col_word))])
        words = sum(words, [])
        words = [Word(*word) for word in words if len(word[0]) > 1]

        return words

    def get_words_wo_add(self, tiles_to_add: list[Tile]):
        """
        Return the words formed by the tiles to add without adding them, raise an error if one word is unvalid
        """
        old_words = self.get_words_on_board()
        self.add_tiles(tiles_to_add)
        new_words = self.get_words_on_board()
        self.remove_tiles(tiles_to_add)
        for old_word in old_words:
            if old_word in new_words:
                new_words.remove(old_word)
        if unvalid_words := [word for word in new_words if not word]:
            raise BadWords('Unvalid words detected',
                                bad_words=unvalid_words,good_words=new_words)
        return new_words

    # TODO: Refactor if possible
    def get_score(self, tiles_to_add: list[Tile]):
        """
        Compute and return the score marked by the tiles to add
        """
        new_words = self.get_words_wo_add(tiles_to_add)
        new_tiles_loc = [tile.pos for tile in tiles_to_add]
        for word in new_words:
            for tile in word.tiles:
                if tile.pos in new_tiles_loc:
                    if tile.pos in multipliers['letter_double']:
                        word.score += tile.value
                    if tile.pos in multipliers['letter_triple']:
                        word.score += tile.value * 2
                    if tile.pos in multipliers['word_double']:
                        word.score *= 2
                    if tile.pos in multipliers['word_triple']:
                        word.score *= 3
        return sum(word.score for word in new_words)
