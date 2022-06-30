import random
import uuid

frLettersDistribution = [['*', 2, 0], ['E', 16, 1], ['A', 9, 1], ['I', 8, 1], ['D', 6, 1], ['N', 8, 1], ['O', 6, 1], ['R', 6, 1], ['S', 6, 1], ['T', 6, 1], ['G', 4, 2], [
        'H', 3, 2], ['L', 3, 2], ['K', 3, 3], ['W', 3, 3], ['M', 2, 4], ['U', 2, 4], ['Y', 2, 4], ['P', 2, 5], ['V', 2, 5], ['B', 1, 8], ['F', 1, 8], ['J', 1, 10]]

enLettersDistribution = []

distributionDict = {
    'fr': frLettersDistribution,
    'en': enLettersDistribution
}


class Scrabble:
    """Scrabble class, define scrabble object and methods"""
    def __init__(self, players, purse={}, racks={}, board={}, gridSize=15, tilesPerRack=7, lang='fr'):
        if lang != 'fr': raise Exception("Only french language is handled, others are incoming")
        
        self.players = players
        self.nbPlayers = len(players)
        self.gridSize = gridSize
        self.tilesPerRack = tilesPerRack
        self.lang = lang

        if board == {}:
            self.purse = self.__createInitialPurse()
            self.racks = self.__drawInitialRacks()
            self.board = {}
        else:
            self.purse = purse
            self.racks = racks
            self.board = board

        self.tilesInPurse = len(purse)


    def __str__(self) -> str:
        return f"Scrabble game: {len(self.players)} joueurs, {self.gridSize}*{self.gridSize}"

    def __createInitialPurse(self):
        distribution = distributionDict[self.lang]
        initialPurse = []
        for letter in distribution:
            initialPurse += [{'letter': letter[0], 'point': letter[2],'id': str(uuid.uuid4())} for _ in range(letter[1])]
        
        random.shuffle(initialPurse)
        return initialPurse

    def __drawInitialRacks(self):
        racks = []
        for player in self.players:
            tiles = []
            for i in range(self.tilesPerRack):
                tile = self.purse.pop()
                tile['isSelected'] = False
                tile['isLocked'] = False
                tile['location'] = {'place': 'rack', 'coords': i}
                tiles.append(tile)
            racks.append({'playerID': player['id'], 'tiles': tiles})
        self.tilesInPurse = len(self.purse)
        return racks


    def drawTile(self):
        print('public tile')
        self.__drawTile()

    def __drawTile(self, player):
        tile = self.purse.pop()
        tile['isSelected'] = False
        tile['isLocked'] = False
        tile['location'] = {'place': 'rack', 'coords': 37}
        return tile

players = [
  {'id': 'id0', 'pseudo': 'pseudo0'},
  {'id': 'id1', 'pseudo': 'pseudo1'}
]

scrabble = Scrabble('name', players)

print(scrabble)
print(len(scrabble.purse))
print(scrabble.racks)

# scrabble.drawTile()
from pprint import pprint
print(Scrabble.__dict__)