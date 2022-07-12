class ScrabbleError(Exception):
    pass


class UnavailableLanguage(ScrabbleError):
    pass


class EmptyPurse(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('Purse is empty')


class NoCenter(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('No tile on board center')

class UnalignedTiles(ScrabbleError):
    def __init__(self) -> None:
        super().__init__('Tiles are unaligned')


class BoardOverlap(ScrabbleError):
    def __init__(self, overlap_coord: tuple) -> None:
        super().__init__('Tile Overlap')
        self.overlap_pos = overlap_coord


class BadWords(ScrabbleError):
    def __init__(self, message: str, good_words: list, bad_words: list) -> None:
        super().__init__(message)
        self.good_words = good_words
        self.bad_words = bad_words
