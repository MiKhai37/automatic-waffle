from ScrabbleLogic import Tile,Purse,Board, Word


purse = Purse()
purse.draw()


maison = Word('maison', [3,4])
macon = Word('macon', [3,4], 'H')

words = maison + macon + [Tile('H', [4,5])]

board = Board(words)
print(board)
print(board.words_on_board())

def is_same_words(words, other_words):
    if len(words) != len(other_words):
        return False

    words = [word.upper() for word in words]
    other_words = [word.upper() for word in other_words]
    
    for word in words:
        if word not in other_words:
            return False
        else:
            other_words.remove(word)
    return True

print(is_same_words(['maison', 'bike', 'maison'], ['maison', 'maison', 'bike']))
#board_sum = Board() + Board()
