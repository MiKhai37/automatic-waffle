import random
from .helpers import create_distribution
from .tile import Tile
from ..errors import ScrabbleError


class Purse:
    def __init__(self, tiles: list[Tile] = None, lang: str = 'fr'):
        self.lang = lang
        self.tiles = self.__init_purse() if tiles is None else tiles.copy()

    def __init_purse(self):
        init_dist = create_distribution(self.lang, 'dict')
        initial_purse = []
        for letter in init_dist:
            initial_purse.extend(Tile(letter)
                                 for _ in range(init_dist[letter]['count']))
        random.shuffle(initial_purse)
        return initial_purse

    def __len__(self):
        return len(self.tiles)

    def __str__(self):
        return(str(self.get_dist()))

    def get_dist(self):
        init_dist = create_distribution(lang=self.lang, format='dict')
        available = {}
        for letter in init_dist:
            count = sum(tile.letter == letter for tile in self.tiles)
            available[letter] = count
        return available

    def draw(self, n=1):
        if len(self) < n:
            raise ScrabbleError(
                f'Not enough tiles in purse, {len(self)} in the purse')
        return [self.tiles.pop() for _ in range(n)] if n > 1 else self.tiles.pop()
