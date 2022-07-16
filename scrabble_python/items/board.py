from pprint import pformat
from itertools import repeat

from scrabble_python.errors import (BadWords, BoardOverlap, NoCenter, NoContact, OutOfBoard,
                                    ScrabbleError, UnalignedTiles)

from .tile import Tile
from .word import Word

letter_magic = {
    3: [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)],
    2: [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]
}

word_magic = {
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
        return f'Board({str(self.get_words())})'

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
        board_pos = [tile.pos for tile in self.tiles]
        add_pos = [tile.pos for tile in tiles_to_add]
        xs = [pos[0] for pos in add_pos]
        ys = [pos[1] for pos in add_pos]
        # Added tiles must be on board:
        if any(coord < 0 or coord > self.SIZE-1 for coord in xs + ys):
            raise OutOfBoard
        # First added tiles must hit the center
        if len(self) == 0 and (self.CENTER, self.CENTER) not in add_pos:
            raise NoCenter
        # Added tiles must not overlap
        if any(coord_to_add in board_pos for coord_to_add in add_pos):
            raise BoardOverlap
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
            row_index = self.__get_word_start(row)
            row_pos = zip(repeat(x, len(row_index)), row_index)
            words.extend(zip(''.join(row).split(), row_pos,
                         repeat('H', len(row_index))))
        for y, col in enumerate(cols):
            col_index = self.__get_word_start(col)
            col_pos = zip(col_index, repeat(y, len(col_index)))
            words.extend(zip(''.join(col).split(), col_pos,
                         repeat('V', len(col_index))))

        return [Word(*word) for word in words if len(word[0]) > 1]

    def get_next_words(self, next_tiles: list[Tile]) -> list[Word]:
        """
        Return the words formed by the tiles to add without adding them
        Raise a BadWords Error if one word is unvalid
        """
        prev_words = self.get_words()
        self.add_tiles(next_tiles)
        curr_words = self.get_words()
        self.remove_tiles(next_tiles)
        next_words = [word for word in curr_words if word not in prev_words]
        if bad_words := [word for word in next_words if not word]:
            good_words = [word for word in next_words if word]
            raise BadWords(good_words=good_words, bad_words=bad_words)
        if not next_words:
            raise ScrabbleError('No words')
        return next_words

    def get_points(self, next_tiles: list[Tile]) -> int:
        """
        Compute and return the score marked by the tiles to add
        """
        next_words = self.get_next_words(next_tiles)
        next_pos = [tile.pos for tile in next_tiles]
        for word in next_words:
            # First compute double/triple letters
            word_add_tiles = [
                tile for tile in word.tiles if tile.pos in next_pos]
            for tile in word_add_tiles:
                magic_letter_pos = sum(letter_magic.values(), [])
                if tile.pos in magic_letter_pos:
                    mult = [mult for mult in letter_magic.keys(
                    ) if tile.pos in letter_magic[mult]][0]
                    word.score += tile.value * (mult - 1)
            # Then compute double/triple words
            for tile in word_add_tiles:
                magic_word_pos = sum(word_magic.values(), [])
                if tile.pos in magic_word_pos:
                    mult = [mult for mult in word_magic.keys(
                    ) if tile.pos in word_magic[mult]][0]
                    word.score *= mult
        return sum((word.score for word in next_words), 0)
