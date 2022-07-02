from word_detection import detect_words, validate_words, score_words, get_board_space, create_reduced_board

validBoard = [
    {'letter': 'M', 'location': {'coords': [7, 7]}},
    {'letter': 'A', 'location': {'coords': [7, 8]}},
    {'letter': 'I', 'location': {'coords': [7, 9]}},
    {'letter': 'S', 'location': {'coords': [7, 10]}},
    {'letter': 'O', 'location': {'coords': [7, 11]}},
    {'letter': 'N', 'location': {'coords': [7, 12]}},
    {'letter': 'B', 'location': {'coords': [6, 9]}},
    {'letter': 'T', 'location': {'coords': [8, 9]}},
    {'letter': 'E', 'location': {'coords': [9, 9]}},
]

unvalidBoard = [
    {'letter': 'M', 'location': {'coords': [7, 7]}},
    {'letter': 'K', 'location': {'coords': [7, 8]}},
    {'letter': 'I', 'location': {'coords': [7, 9]}},
    {'letter': 'S', 'location': {'coords': [7, 10]}},
    {'letter': 'O', 'location': {'coords': [7, 11]}},
    {'letter': 'N', 'location': {'coords': [7, 12]}},
    {'letter': 'B', 'location': {'coords': [6, 9]}},
    {'letter': 'T', 'location': {'coords': [8, 9]}},
    {'letter': 'E', 'location': {'coords': [9, 9]}},
]

littleBoard = [
    {'letter': 'O', 'location': {'coords': [7, 7]}},
    {'letter': 'U', 'location': {'coords': [7, 8]}},
    {'letter': 'I', 'location': {'coords': [7, 9]}},
    {'letter': 'N', 'location': {'coords': [6, 7]}},
    {'letter': 'N', 'location': {'coords': [8, 7]}},
]


def test_get_board_space():
    assert get_board_space(validBoard) == [4, 6, 6, 7]
    assert get_board_space(littleBoard) == [3, 6, 3, 7]


def test_create_board():
    assert [len(create_reduced_board(validBoard)), len(
        create_reduced_board(validBoard)[0])] == [4, 6]
    assert create_reduced_board(littleBoard) == [['N', ' ', ' '], [
        'O', 'U', 'I'], ['N', ' ', ' ']]


def test_detect_words():
    assert detect_words(littleBoard) == ['OUI', 'NON']
    assert detect_words(validBoard) == ['MAISON', 'BITE']
    assert detect_words(unvalidBoard) == ['MKISON', 'BITE']


def test_valid_words():
    assert validate_words(detect_words(validBoard))[0] == True
    assert validate_words(detect_words(littleBoard))[0] == True
    assert validate_words(detect_words(unvalidBoard))[0] == False


def test_score_words():
    assert score_words(detect_words(validBoard)) == 13
    assert score_words(detect_words(littleBoard)) == 6
