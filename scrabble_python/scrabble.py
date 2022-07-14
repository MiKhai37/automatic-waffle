import random
from .errors import EmptyPurse, ScrabbleError, UnavailableLanguage
from .helpers import get_avail_langs
from .items import Board, Player, Purse


class Scrabble:
    df_board_size = 15
    df_rack_size = 7
    df_lang = 'fr'
    df_players = [
        Player('player_1'),
        Player('player_2')
    ]

    def __init__(self, players: list[Player] = None, purse: Purse = None, board: Board = None, **scrabble_config) -> None:
        if players is None:
            players = Scrabble.df_players

        self.players = {player.player_id: player for player in players}

        self.players_ids = [*self.players.keys()]
        self.nb_players = len(self.players)
        if self.nb_players > 4:
            raise ScrabbleError('4 players max')

        self.board_size = scrabble_config.get('board_size', Scrabble.df_board_size)
        self.rack_size = scrabble_config.get('rack_size', Scrabble.df_rack_size)
        self.lang = scrabble_config.get('lang', Scrabble.df_lang)
        if self.lang not in get_avail_langs():
            raise UnavailableLanguage(unavail_lang=self.lang)

        self.purse = purse
        self.board = board
        if purse is None or board is None:
            self.__initialize_game()
        self.purse_is_empty = len(self.purse) == 0
        self.turn = 0
        self.turn_rand = random.randint(0, self.nb_players-1)
        self.turn_id = self.players_ids[(
            self.turn + self.turn_rand) % self.nb_players]

    def __initialize_game(self):
        self.purse = Purse(lang=self.lang)
        self.board = Board(size=self.board_size)
        for _ in range(self.rack_size):
            for player_id in self.players:
                self.players[player_id].rack.extend(self.purse.draw())

    def submit(self, move):
        try:
            print('move submission')
            new_word = self.board.get_words_wo_add(move)
        except ScrabbleError as e:
            print('move NOT OK')
            print(f'error type: {type(e).__name__}')
            print(e.args)
        else:
            print('move OK')
            print('New words:')
            print('Score:')
            # self.board.add_tiles(move)
            self.turn += 1
            self.turn_id = self.players_ids[(
                self.turn + self.turn_rand) % self.nb_players]
        finally:
            scores = [player.score for player in self.players]
            print(*zip(self.players_ids, scores))
            print(self.turn_id)

    def cli_play(self):
        raise NotImplementedError
