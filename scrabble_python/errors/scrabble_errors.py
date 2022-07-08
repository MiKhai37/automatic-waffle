class ScrabbleError(Exception):
    pass

class EmptyPurse(ScrabbleError):
    pass

class BoardOverlap(ScrabbleError):
    pass