from scrabble_python.items.helpers import get_avail_langs
from scrabble_python.items import Player
from scrabble_python.items import Board
from scrabble_python.items import Purse
from scrabble_python.errors import ScrabbleError


class Scrabble:
    df_board_size = 15
    df_rack_size = 7
    df_lang = 'fr'

    def __init__(self, players: list[Player] = None, purse: Purse = None, board: Board = None, **scrabble_config) -> None:
        lang = scrabble_config.get('lang')
        board_size = scrabble_config.get('board_size')
        rack_size = scrabble_config.get('rack_size')
        avail_langs = get_avail_langs()
        if lang is not None and lang not in avail_langs:
            raise ScrabbleError(
                f'language not available, available languages: {avail_langs}')
        self.lang = Scrabble.df_lang if lang is None else lang
        self.board_size = Scrabble.df_board_size if board_size is None else board_size
        self.rack_size = Scrabble.df_rack_size if rack_size is None else rack_size

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

    def submit(self, move):
        pass
