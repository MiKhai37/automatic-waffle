import random
from scrabble_python.errors import EmptyPurse, ScrabbleError
from scrabble_python.helpers import create_distribution
from .tile import Tile


class Purse:
    def __init__(self, tiles: list[Tile] = None, lang: str = 'fr') -> None:
        self.lang = lang
        self.tiles = self.__init_purse() if tiles is None else tiles.copy()

    def __init_purse(self) -> list[Tile]:
        init_dist = create_distribution(self.lang, 'dict')
        initial_purse = []
        for letter in init_dist:
            initial_purse.extend([Tile(letter)] * init_dist[letter]['count'])
        random.shuffle(initial_purse)
        return initial_purse

    def __len__(self) -> int:
        return len(self.tiles)

    def __str__(self) -> str:
        return(str(self.get_dist()))

    def __repr__(self) -> str:
        return(f'Purse: {str(self.get_dist())}')

    def get_dist(self) -> dict:
        """
        Return the letter distribution in the purse
        """
        init_dist = create_distribution(lang=self.lang, format='dict')
        return {letter: sum(tile.letter == letter for tile in self.tiles) for letter in init_dist}

    def draw(self, n=1) -> list[Tile]:
        drawn_tiles = []
        for _ in range(n):
            if len(self) == 0:
                raise EmptyPurse
            drawn_tiles.append(self.tiles.pop())
        return drawn_tiles
