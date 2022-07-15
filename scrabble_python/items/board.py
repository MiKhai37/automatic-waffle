from pprint import pformat

from scrabble_python.errors import (BadWords, BoardOverlap, NoCenter, NoContact, OutOfBoard,
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
        self.SIZE = size
        self.CENTER = self.SIZE // 2
        self.tiles: list[Tile] = []
        if tiles is not None:
            self.add_tiles(tiles)

    def __str__(self) -> str:
        board = self.__format_board()
        return pformat(board)

    def __repr__(self) -> str:
        return str(self.get_words())

    def __len__(self) -> int:
        return len(self.tiles)

    def __eq__(self, other) -> bool:
        s_words = self.get_words()
        o_words = other.get_words()
        return isinstance(other, Board) \
            and all(word in o_words for word in s_words) \
            and all(word in s_words for word in o_words)

    def __format_board(self) -> list[list[str]]:
        """
        Create and return a representation of the board in a list format
        """
        row = [' '] * self.SIZE
        board = [row.copy() for _ in range(self.SIZE)]
        for tile in self.tiles:
            board[tile.pos[0]][tile.pos[1]] = tile.letter
        return board

    def add_tiles(self, tiles_to_add: list[Tile]) -> None:
        board_tiles_pos = [tile.pos for tile in self.tiles]
        tiles_to_add_pos = [tile.pos for tile in tiles_to_add]
        xs = [pos[0] for pos in tiles_to_add_pos]
        ys = [pos[1] for pos in tiles_to_add_pos]
        # Added tiles must be on board:
        if any(coord < 0 or coord > self.SIZE-1 for coord in xs + ys):
            raise OutOfBoard
        # First added tiles must hit the center
        if len(self) == 0 and (self.CENTER, self.CENTER) not in tiles_to_add_pos:
            raise NoCenter
        # Added tiles must not overlap
        for coord_to_add in tiles_to_add_pos:
            if coord_to_add in board_tiles_pos:
                raise BoardOverlap(overlap_coord=coord_to_add)
        # Added tiles must be on same line
        if max(xs) - min(xs) != 0 and max(ys) - min(ys) != 0:
            raise UnalignedTiles
        # Added tiles must be in contact with board tiles
        if len(self) != 0 and not self.check_contact(tiles_to_add):
            raise NoContact
        self.tiles.extend(tiles_to_add)

    def check_contact(self, tiles_to_add):
        board_tiles_pos = [tile.pos for tile in self.tiles]
        plus_x_pos = [(pos[0] + 1, pos[1]) for pos in board_tiles_pos]
        minus_x_pos = [(pos[0] - 1, pos[1]) for pos in board_tiles_pos]
        plus_y_pos = [(pos[0], pos[1] + 1) for pos in board_tiles_pos]
        minus_y_pos = [(pos[0], pos[1] - 1) for pos in board_tiles_pos]
        contact_pos = set(plus_x_pos + minus_x_pos + plus_y_pos + minus_y_pos)
        return any(tile.pos in contact_pos for tile in tiles_to_add)

    def remove_tiles(self, tiles_to_remove: list[Tile]) -> None:
        for tile in tiles_to_remove:
            if tile not in self.tiles:
                raise ScrabbleError('tile not in board tiles')
            self.tiles.remove(tile)

    def __get_word_start(self, row_or_col: list[str]) -> list[int]:
        """
        Return the start postion of words on a row or a column
        """
        row_or_col = [' '] + row_or_col
        return [i for i, [prev, curr] in enumerate(zip(row_or_col, row_or_col[1:]))
                if prev == ' ' and curr != ' ']

    def get_words(self) -> list[Word]:
        """
        Return list[Word] corresponding to the words present on the board in
        """
        rows = self.__format_board()
        cols = [[row[i] for row in rows] for i in range(self.SIZE)]
        words = []
        for x, row in enumerate(rows):
            row_words = ''.join(row).split()
            row_index = self.__get_word_start(row)
            row_coords = [*zip([x]*len(row_index), row_index)]
            words.extend([*zip(row_words, row_coords, ['H']*len(row_words))])
        for y, col in enumerate(cols):
            col_words = ''.join(col).split()
            col_index = self.__get_word_start(col)
            col_coords = [*zip(col_index, [y]*len(col_index))]
            words.extend([*zip(col_words, col_coords, ['V']*len(col_words))])

        return [Word(*word) for word in words if len(word[0]) > 1]

    def get_next_words(self, tiles_to_add: list[Tile]) -> list[Word]:
        """
        Return the words formed by the tiles to add without adding them
        Raise a BadWords Error if one word is unvalid
        """
        prev_words = self.get_words()
        self.add_tiles(tiles_to_add)
        curr_words = self.get_words()
        self.remove_tiles(tiles_to_add)
        next_words = [word for word in curr_words if word not in prev_words]
        if bad_words := [word for word in next_words if not word]:
            good_words = [word for word in next_words if word]
            raise BadWords(good_words=good_words, bad_words=bad_words)
        return next_words

    def get_score(self, tiles_to_add: list[Tile]) -> int:
        """
        Compute and return the score marked by the tiles to add
        """
        next_words = self.get_next_words(tiles_to_add)
        next_pos = [tile.pos for tile in tiles_to_add]
        for word in next_words:
            # First compute double/triple letters
            for tile in word.tiles:
                if tile.pos in next_pos:
                    if tile.pos in multipliers['letter_double']:
                        word.score += tile.value
                    if tile.pos in multipliers['letter_triple']:
                        word.score += tile.value * 2
            # Then compute double/triple words
            for tile in word.tiles:
                if tile.pos in next_pos:
                    if tile.pos in multipliers['word_double']:
                        word.score *= 2
                    if tile.pos in multipliers['word_triple']:
                        word.score *= 3
        return sum((word.score for word in next_words), 0)
