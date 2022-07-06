from uuid import uuid4
from .helpers import create_distribution



class Tile:
    def __init__(self, letter: str, pos: tuple = None, tile_id: str = None, lang: str = 'fr'):
        self.lang = lang
        # self.__id = tile_id
        # if tile_id is None:
        #     self.__id = str(uuid4())
        self.letter = letter.upper()
        self.pos = pos
        if pos is not None:
            self.pos = tuple(pos)
            self.x = pos[0]
            self.y = pos[1]
        self.value = self.__get_value()

    # @property
    # def id(self):
    #     return self.__id

    def __get_value(self):
        distribution = create_distribution(self.lang, 'dict')
        return distribution[self.letter]['value']

    def __str__(self) -> str:
        return f'{self.letter}, {self.pos}, points: {self.value}'

    def __repr__(self) -> str:
        return f'Tile({self.letter}, {self.pos}, {self.lang})'

    def __eq__(self, other):
        return isinstance(other, Tile) and self.letter == other.letter and self.pos == other.pos
