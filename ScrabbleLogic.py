import random
import uuid
from pprint import pformat

from scrabble_helpers import createDictionary, createDistribution


class Scrabble:
    """
    Scrabble class, create scrabble game instance

    ```

    Attributes
    ----------
    players : [player]
        List of player object ({id, pseudo})
    purse : [tile]
        List of tiles available for drawing
    """

    def __init__(self, players, purse=None, racks=None, board=None, gridSize=15, tilesPerRack=7, lang='fr'):
        if purse is None:
            purse = []
        if racks is None:
            racks = []
        if board is None:
            board = []
        if lang != 'fr':
            raise NotImplementedError(
                "Only french language is handled for the moment")

        self.players = players
        self.nbPlayers = len(players)
        self.gridSize = gridSize
        self.tilesPerRack = tilesPerRack
        self.lang = lang
        self.history = []

        self.purse = Purse(purse, lang='fr')
        self.racks = racks
        self.board = board
        if purse == []:
            self.racks = self.__drawInitialRacks()
            self.board = []

    def __str__(self) -> str:
        return f"Scrabble game: {len(self.players)} joueurs, {self.gridSize}*{self.gridSize}"

    def __createInitialPurse(self) -> list:
        """
        Create the inital letter purse
            Parameters:
                No
            Returns:
                initialPurse (list): list of all tiles representing the starting purse
        """
        distribution = createDistribution(lang=self.lang, format='list')
        initialPurse = []
        for letter in distribution:
            initialPurse += [{'letter': letter[0], 'point': letter[2],
                              'id': str(uuid.uuid4())} for _ in range(letter[1])]

        # Shuffle once then pop from the end
        # Better than no shuffling then pop from random index
        random.shuffle(initialPurse)
        return initialPurse

    def __drawInitialRacks(self):
        """
        Draw and return initial players racks
        """
        racks = []
        for player in self.players:
            rack = []
            for i in range(self.tilesPerRack):
                tile = self.purse.pop()
                tile['isSelected'] = False
                tile['isLocked'] = False
                tile['location'] = {'place': 'rack', 'coords': i}
                rack.append(tile)
            racks.append({'playerID': player['id'], 'rack': rack})
        self.tilesInPurse = len(self.purse)
        return racks

    def __drawTile(self, player, nbTiles):
        """Draw required number of tiles from the purse and return it"""
        tile = self.purse.pop()
        tile['isSelected'] = False
        tile['isLocked'] = False
        tile['location'] = {'place': 'rack', 'coords': 37}
        return tile

    def moveSubmit(self, move):
        """
        Handle move submission,
        if legal,
            save move
            score points
            draw tiles
            return drawn tiles and scored points
        if illegal,
            block move
            return illegal causes
        """
        if not self._isLegit(move):
            return False
        words = self._findWords(move)
        points = self._calculateScoredPoints(words)
        tilesToDraw = 0
        tiles = self.__drawTile(move, tilesToDraw)
        return tiles, points

    def _isLegit(self, move):
        """Check for illegal moves, like unlegitmate tile mutation"""
        return True

    def _findWords(self, move):
        """Return words created by the move"""
        return []

    def _calculateScoredPoints(self, words):
        """Return the points mark by the move"""
        return 0


class Player:
    def __init__(self, name, score=0, id=None) -> None:
        self.name = name
        self.score = score
        self.id = id
        if id is None:
            self.id = str(uuid.uuid4())


class Tile(dict):
    def __init__(self, letter=' ', loc=None, lang='fr') -> None:
        self.__lang = lang
        # self['id'] = str(uuid.uuid4())
        # self.id = self['id']
        self['letter'] = letter
        self.letter = self['letter']
        self['loc'] = loc
        self.loc = self['loc']
        self['value'] = self.__get_value()
        self.value = self['value']
        if isinstance(loc, list) and len(loc) == 2:
            self.on = 'board'
            self.x, self.y = loc
        elif isinstance(loc, int):
            self.on = 'rack'
            self.x, self.y = [None, None]
        else:
            self.on = 'purse'
            self.x, self.y = [None, None]

    def __get_value(self):
        distribution = createDistribution(self.__lang, 'dict')
        return distribution[self['letter']]['value']


class Board:
    def __init__(self, tiles: list[Tile] = None, size=15) -> None:
        if tiles is None:
            tiles = []
        for tile in tiles:
            if type(tile) != Tile:
                raise TypeError(f'{tile} is not a Tile object')
            if tile.on != 'board':
                raise AttributeError(f'{tile} is not on board')
        self.tiles = tiles
        self.size = size

    def __repr__(self) -> str:
        reduced_board = self.__create_reduced_board()
        return pformat(reduced_board)

    def __eq__(self, other: object) -> bool:
        if len(other.tiles) != len(self.tiles):
            return False
        tiles_copy = self.tiles.copy()
        __o_tiles_copy = other.tiles.copy()
        for tile in tiles_copy:
            if tile not in __o_tiles_copy:
                return False
            else:
                __o_tiles_copy.remove(tile)
        return True

    def add(self, other):
        if type(other) == Tile:
            self.tiles.append(other)
        elif type(other) == Word:
            self.tiles += other
        else:
            raise TypeError(
                'add method only supported for <Tile> and <Word> Types')
    # TODO: check if occupied to avoid overwrite with add method

    def remove(self, other):
        if type(other) == Tile:
            self.tiles.remove(other)
        elif type(other) == Word:
            for tile in other:
                self.tiles.remove(tile)
        else:
            raise TypeError(
                'remove method only supported for <Tile> and <Word> Types')

    def __board_space(self):
        coords = list(map(lambda tile: tile.loc, self.tiles))
        x_coords = list(map(lambda coord: coord[0], coords))
        y_coords = list(map(lambda coord: coord[1], coords))
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        x_size = x_max - x_min + 1
        y_size = y_max - y_min + 1
        return [x_size, x_min, y_size, y_min]

    def __create_reduced_board(self):
        x_size, x_min, y_size, y_min = self.__board_space()
        row = [' '] * y_size
        reduced_board = [row.copy() for _ in range(x_size)]
        for tile in self.tiles:
            letter = tile.letter
            idx = tile.x - x_min
            idy = tile.y - y_min
            reduced_board[idx][idy] = letter
        return reduced_board

    def create_board(self):
        row = [' '] * self.size
        board = [row.copy() for _ in range(self.size)]
        for tile in self.tiles:
            board[tile.x][tile.y] = tile.letter
        return board

    def words_on_board(self, full=False):
        rows = self.__create_reduced_board()
        if full:
            rows = self.create_board()
        #rows = self.create_board()
        cols = [[row[i] for row in rows] for i in range(len(rows[0]))]
        cols_and_rows = rows + cols
        whitespaced_strings = [''.join(line) for line in cols_and_rows]
        strings = list(map(lambda string: string.split(), whitespaced_strings))
        flat_strings = sum(strings, [])
        return list(filter(lambda word: len(word) > 1, flat_strings))

    def compare_words(self, word_or_tile):
        old_words = self.words_on_board()
        self.add(word_or_tile)
        new_words = self.words_on_board()
        self.remove(word_or_tile)
        for old_word in old_words:
            if old_word in new_words:
                new_words.remove(old_word)
        return new_words



class Purse:
    def __init__(self, tiles=None, lang='fr') -> None:
        if tiles is None:
            tiles = []
        self.__lang = lang
        self.__tiles = tiles
        if tiles == []:
            self.__tiles: list[Tile] = self.__createInitialPurse()
        self.count = len(self.__tiles)

    def __createInitialPurse(self) -> list[Tile]:
        """
        Create the inital letter purse
        """
        distribution = createDistribution(lang=self.__lang, format='list')
        initial_purse = []
        for letter in distribution:
            initial_purse += [Tile(letter=letter[0])
                              for _ in range(letter[1])]
        # Shuffle once then pop from the end
        # Better than no shuffling then pop from random index
        random.shuffle(initial_purse)
        return initial_purse

    def get_letters_in(self):
        distribution = createDistribution(lang=self.__lang, format='list')
        letters = [letter[0] for letter in distribution]
        available = {}
        for letter in letters:
            count = sum(tile['letter'] == letter for tile in self.__tiles)
            available[letter] = count
        return available

    def draw(self):
        if self.count == 0:
            raise IndexError('empty purse')
        tile = self.__tiles.pop()
        self.count -= 1
        return tile

    def draw_n(self, n):
        return [self.draw() for _ in range(n)]


class Word(list[Tile]):
    def __init__(self, text='word', start=None, orientation='V'):
        if start is None:
            start = [0, 0]
        self.text = text.upper()
        self.start = start
        if orientation not in ['V','H',0,1]:
            raise ValueError(
                'orientation is (H or 0)for Horizontal, or V (or 1) for Vertical')
        for i, lettre in enumerate(self.text):
            if orientation in ['H', 0]:
                self.append(Tile(lettre, [start[0], start[1]+i]))
            elif orientation in ['V', 1]:
                self.append(Tile(lettre, [start[0]+i, start[1]]))
        self.end = self[-1].loc

    def __str__(self) -> str:
        return f'{self.text}: {self.start} -> {self.end}'

    def __repr__(self) -> str:
        return f'Word: {str(self)}'
