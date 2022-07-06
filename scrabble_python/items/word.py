from .tile import Tile
from .helpers import create_dictionary


class Word:
    def __init__(self, text: str, start: list, orientation='H', lang='fr'):
        self.score = 0
        self.text = text.upper()
        self.lang = lang
        self.start = tuple(start)
        if orientation not in ['V', 'H', 0, 1]:
            raise ValueError(
                'orientation is (H or 0)for Horizontal, or V (or 1) for Vertical')
        self.orientation = orientation
        if orientation in ['H', 0]:
            self.tiles = [Tile(lettre, (start[0], start[1] + i))
                          for (i, lettre) in enumerate(self.text)]
        else:
            self.tiles = [Tile(lettre, (start[0] + i, start[1]))
                          for (i, lettre) in enumerate(self.text)]
        self.end = self.tiles[-1].pos
        self.score = self.__get_initial_score()

    def __str__(self) -> str:
        return f'{self.text}: {self.start} -> {self.end}'

    def __repr__(self) -> str:
        return f'Word({self.text}, {self.start}, {self.orientation})'

    def __len__(self):
        return len(self.tiles)

    def __bool__(self):
        dico = create_dictionary(self.lang)
        return self.text.lower() in dico

    def __eq__(self, other) -> int:
        return isinstance(other, Word) and self.text == other.text and self.start == other.start and self.end == other.end

    def __get_initial_score(self):
        values = [tile.value for tile in self.tiles]
        return sum(values)
