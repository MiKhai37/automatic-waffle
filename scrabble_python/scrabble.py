import random
from .errors import EmptyPurse, ScrabbleError, UnavailableLanguage
from .helpers import get_avail_langs
from .items import Board, Player, Purse, Word


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
        if len(players) > 4:
            raise ScrabbleError('4 players max')

        self.players = {player.player_id: player for player in players}
        self.players_ids = [*self.players.keys()]
        self.nb_players = len(self.players)

        self.BOARD_SIZE = scrabble_config.get(
            'board_size', Scrabble.df_board_size)
        self.RACK_SIZE = scrabble_config.get(
            'rack_size', Scrabble.df_rack_size)
        self.LANG = scrabble_config.get(
            'lang', Scrabble.df_lang)
        if self.LANG not in get_avail_langs():
            raise UnavailableLanguage(unavail_lang=self.LANG)

        self.purse = purse
        self.board = board
        if purse is None or board is None:
            self.__initialize_game()
        self.turn = 0
        self.turn_rand = random.randint(0, self.nb_players-1)
        self.turn_id = self.__get_turn_id()
        self.history = {}

    def __initialize_game(self) -> None:
        self.purse = Purse(lang=self.LANG)
        self.board = Board(size=self.BOARD_SIZE)
        for _ in range(self.RACK_SIZE):
            for player_id in self.players:
                rack = self.players[player_id].rack
                rack.extend(self.purse.draw())

    def __get_turn_id(self) -> str:
        return self.players_ids[(self.turn + self.turn_rand) % self.nb_players]

    def __save_move(self, move) -> None:
        new_words = self.board.get_next_words(move)
        self.history[self.turn] = new_words
        scored_points = self.board.get_score(move)
        self.players[self.turn_id].score += scored_points
        self.board.add_tiles(move)
        self.turn += 1
        self.turn_id = self.__get_turn_id()

    def display_info(self) -> None:
        scores = [self.players[player_id].score for player_id in self.players_ids]
        print('Scores:')
        print(*zip(self.players_ids, scores))
        print('Board:')
        print(self.board)
        print(f'Player turn: {self.turn_id}')
        print('Player rack:')
        print(self.players[self.turn_id].rack)

    def submit(self, move) -> None:
        try:
            print('move submission')
            new_word = self.board.get_next_words(move)
        except ScrabbleError as e:
            print('move NOT OK')
            print(f'error type: {type(e).__name__}')
            print(e.args)
        else:
            print('move OK')
            self.__save_move(move)
        finally:
            self.display_info()

    def cli_play(self):
        raise NotImplementedError
