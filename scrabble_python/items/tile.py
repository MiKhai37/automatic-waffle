from scrabble_python.helpers import create_distribution


class Tile:
    def __init__(self, letter: str, pos: tuple = None, lang: str = 'fr'):
        self.lang = lang
        self.letter = letter.upper()
        self.pos = pos
        if pos is not None:
            self.pos = tuple(pos)
        self.value = self.__get_value()

    def __get_value(self):
        distribution = create_distribution(self.lang, 'dict')
        return distribution[self.letter]['value']

    def __str__(self) -> str:
        return f'{self.letter}, {self.pos}, value: {self.value}'

    def __repr__(self) -> str:
        return f'Tile({self.letter}, {self.pos}, {self.lang})'

    def __eq__(self, other):
        return isinstance(other, Tile) \
            and self.letter == other.letter \
            and self.pos == other.pos
