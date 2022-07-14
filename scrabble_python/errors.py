from .helpers import get_avail_langs


class ScrabbleError(Exception):
    pass


class UnavailableLanguage(ScrabbleError):
    def __init__(self, unavail_lang: str) -> None:
        super().__init__(f'{unavail_lang}: this language is unavailable')
        self.unavail_lang = unavail_lang
        self.avail_langs = get_avail_langs()


class EmptyPurse(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('No more tiles in purse')


class NoCenter(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('No tile on board center')


class UnalignedTiles(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('Placed tiles are unaligned (not on a same row or column)')


class BoardOverlap(ScrabbleError):
    def __init__(self, overlap_coord: tuple) -> None:
        super().__init__('Some tiles are overlapping')
        self.overlap_pos = overlap_coord

class NoContact(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('Added tiles must be in contact with other tiles')

class OutOfBoard(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('Tile are out of the board')

class BadWords(ScrabbleError):
    def __init__(self, good_words: list, bad_words: list) -> None:
        super().__init__('Some words do not exist')
        self.good_words = good_words
        self.bad_words = bad_words