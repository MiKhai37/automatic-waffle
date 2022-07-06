from .items import Player
from .items import Board
from .items import Purse
from .errors import ScrabbleError


class Scrabble:
    def __init__(self, players: list[Player] = None, purse: Purse = None, board: Board = None, **scrabble_config) -> None:
        self.lang = scrabble_config['lang']
        self.board_size = scrabble_config['board_size']
        self.rack_size = scrabble_config['rack_size']

        self.players = players
        if self.players is None:
            self.players = [
                Player('player_1'),
                Player('player_2')
            ]
        self.nb_players = len(self.players)
        if self.nb_players > 4:
            raise ScrabbleError('4 players max')

        self.purse = purse
        self.board = board
        if purse is None or board is None:
            self.__initialize_game()
        self.purse_is_empty = len(self.purse) == 0

    def __initialize_game(self):
        self.purse = Purse(lang=self.lang)
        self.board = Board(size=self.board_size)
        for _ in range(self.rack_size):
            for player in self.players:
                player.rack.append(self.purse.draw())
