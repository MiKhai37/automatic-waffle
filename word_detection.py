from helpers import createDictionary, createDistribution


def get_board_space(board_tiles):
    tile_coords = list(
        map(lambda tile: tile['location']['coords'], board_tiles))
    x_coords = list(map(lambda coord: coord[0], tile_coords))
    y_coords = list(map(lambda coord: coord[1], tile_coords))
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    x_size = x_max - x_min + 1
    y_size = y_max - y_min + 1
    #print(f'Taille du plateau réduit, x: {x_size}, y: {y_size}, x_min: {x_min}, y_min: {y_min}')
    return [x_size, x_min, y_size, y_min]


def create_reduced_board(board_tiles):
    x_size, x_min, y_size, y_min = get_board_space(board_tiles)
    row = [' '] * y_size
    board = [row.copy() for _ in range(x_size)]
    for tile in board_tiles:
        letter = tile['letter']
        x = tile['location']['coords'][0] - x_min
        y = tile['location']['coords'][1] - y_min
        board[x][y] = letter
    return board

# TODO: need to return the coords of word for score counting (multiplier)


def detect_words(board_tiles):
    """Detect words on board (combination of two letters or more)"""
    board = create_reduced_board(board_tiles)
    rows = board
    cols = []
    for i in range(len(rows)):
        cols.append([row[i] for row in rows])
    cols_and_rows = rows + cols
    whitespaced_strings = list(map(lambda arr: ''.join(arr), cols_and_rows))
    strings = list(map(lambda string: string.split(), whitespaced_strings))
    flat_strings = sum(strings, [])
    words = list(filter(lambda word: len(word) > 1, flat_strings))
    return words


def detect_new_words(new_board_tiles, old_board_tiles):
    """Detect only new words"""
    old_words = detect_words(old_board_tiles)
    new_words = detect_words(new_board_tiles + old_board_tiles)
    for old_word in old_words:
        if old_word in new_words:
            new_words.remove(old_word)
    return new_words


def validate_words(words):
    isValid = True
    scrabbleDict = createDictionary('fr')
    valid_words = []
    unvalid_words = []
    for word in words:
        if word.lower() in scrabbleDict:
            valid_words.append(word)
        else:
            isValid = False
            unvalid_words.append(word)
    return isValid, valid_words, unvalid_words

# TODO: Need to handle with score multiplier


def score_words(words):
    scrabbleDist = createDistribution(lang='fr', format='dict')
    print(scrabbleDist)
    score = 0
    for word in words:
        for letter in word:
            print(letter)
            score += scrabbleDist[letter]['value']
    return score
