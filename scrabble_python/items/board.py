from pprint import pformat
from .tile import Tile
from .word import Word
from ..errors import ScrabbleError

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
        if tiles is None:
            self.tiles = []
        else:
            tiles_pos = [tile.pos for tile in tiles]
            if (7, 7) not in tiles_pos:
                raise ScrabbleError('No tile on the center of the board')
            self.tiles = tiles.copy()

    def __str__(self):
        board = self.__format_board()
        return pformat(board)

    def __len__(self):
        return len(self.tiles)

    def __format_board(self):
        row = [' '] * self.size
        board = [row.copy() for _ in range(self.size)]
        for tile in self.tiles:
            board[tile.x][tile.y] = tile.letter
        return board

    def __eq__(self, other):
        return isinstance(other, Board)

    def add_tiles(self, tiles_to_add: list[Tile]):
        coords_on_board = [tile.pos for tile in self.tiles]
        # First tile must be on center check
        if len(self) == 0 and (self.size//2, self.size//2) not in [tile_to_add.pos for tile_to_add in tiles_to_add]:
            raise ScrabbleError('First tile must be on center')
        # Tile overlap check
        for tile_to_add in tiles_to_add:
            if tile_to_add.pos in coords_on_board:
                raise ScrabbleError(
                    f'Tile overlap: there is already a tile on {tile_to_add.pos}')
        self.tiles += tiles_to_add

    def remove_tiles(self, tiles_to_remove: list[Tile]):
        for tile in tiles_to_remove:
            if tile not in self.tiles:
                raise ScrabbleError('tile not in board tiles')
            self.tiles.remove(tile)

    def __first_index(self, row_or_col: list[str]):
        row_or_col = [' '] + row_or_col
        return [i for i, [prev, curr] in enumerate(zip(row_or_col, row_or_col[1:]))
                if prev == ' ' and curr != ' ']

    def get_words(self) -> list[Word]:
        """
        Returns list[Word] corresponding to the words present on the board in 
        """
        rows = self.__format_board()
        cols = [[row[i] for row in rows] for i in range(len(rows[0]))]
        words = []
        for x, row in enumerate(rows):
            row_word = ''.join(row).split()
            row_index = self.__first_index(row)
            row_coords = [*zip([x]*len(row_index), row_index)]
            words.append([*zip(row_word, row_coords, ['H']*len(row_word))])
        for y, col in enumerate(cols):
            col_word = ''.join(col).split()
            col_index = self.__first_index(col)
            col_coords = [*zip(col_index, [y]*len(col_index))]
            words.append([*zip(col_word, col_coords, ['V']*len(col_word))])
        words = sum(words, [])
        words = [Word(*word) for word in words if len(word[0]) > 1]

        return words

    def get_new_words(self, new_tiles: list[Tile]):
        """
        Return the words formed by the new_tiles, raise an error if one new word is unvalid
        """
        old_words = self.get_words()
        self.add_tiles(new_tiles)
        new_words = self.get_words()
        self.remove_tiles(new_tiles)
        for old_word in old_words:
            if old_word in new_words:
                new_words.remove(old_word)
        # TODO: Find way to retireve the unvalid_words in the ScrabbleError
        if unvalid_words := [word for word in new_words if not word]:
            raise ScrabbleError('Unvalid words detected',
                                unvalid_words, new_words)
        return new_words

    # TODO: Refactor if possible
    def get_score(self, new_tiles: list[Tile]):
        new_words = self.get_new_words(new_tiles)
        new_tiles_loc = [tile.pos for tile in new_tiles]
        for word in new_words:
            for tile in word.tiles:
                if tile.pos in new_tiles_loc:
                    if tile.pos in multipliers['letter_double']:
                        print('letter double')
                        word.score += tile.value
                    if tile.pos in multipliers['letter_triple']:
                        print('letter triple')
                        word.score += tile.value * 2
                    if tile.pos in multipliers['word_double']:
                        print('word double')
                        word.score *= 2
                    if tile.pos in multipliers['word_triple']:
                        print('word triple')
                        word.score *= 3
        return sum(word.score for word in new_words)
