import random as rd
from copy import deepcopy
from itertools import groupby

from .errors import (BadWords, EmptyPurse, NotInRack, ScrabbleError,
                     UnavailableLanguage)
from .helpers import get_avail_langs
from .items import Board, Player, Purse, Tile, Word


class Scrabble:
    df_bsize = 15
    df_rsize = 7
    df_lang = 'fr'
    df_players = [
        Player('player_1'),
        Player('player_2')
    ]

    def __init__(self, **params) -> None:
        players = params.get('players', Scrabble.df_players)
        if len(players) > 4:
            raise ScrabbleError('4 players max')

        self.players = {player.ID: player for player in players}
        self.pl_ids = [*self.players.keys()]
        self.nb_plys = len(self.players)

        self.config = {
            'BOARD_SIZE': params.get('board_size', Scrabble.df_bsize),
            'RACK_SIZE': params.get('rack_size', Scrabble.df_rsize),
            'LANG': params.get('lang', Scrabble.df_lang)
        }

        if self.config['LANG'] not in get_avail_langs():
            raise UnavailableLanguage(unavail_lang=self.config['LANG'])

        self.turn = params.get('turn', 0)
        self.turn_rd = params.get('turn_rd', rd.randint(0, self.nb_plys-1))
        self.curr_player = self.get_curr_player()
        self.history = params.get('history', {})

        self.purse = params.get('purse', None)
        self.board = params.get('board', None)
        if self.purse is None or self.board is None:
            self.__initialize_game()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Scrabble) and self.players == __o.players and self.turn == __o.turn and self.curr_player == __o.curr_player and self.history == __o.history and self.purse == __o.purse and self.board == __o.board

    def __initialize_game(self) -> None:
        self.purse = Purse(lang=self.config['LANG'])
        self.board = Board(size=self.config['BOARD_SIZE'])
        for pl_id in self.players:
            self.players[pl_id].rack.clear()
        for _ in range(self.config['RACK_SIZE']):
            for player_id in self.players:
                rack = self.players[player_id].rack
                rack.extend(self.purse.draw())

    def get_curr_rack(self):
        return self.players[self.curr_player].rack

    def get_curr_player(self) -> str:
        return self.pl_ids[(self.turn + self.turn_rd) % self.nb_plys]

    def save_move(self, move) -> None:
        new_words = self.board.get_next_words(move)
        scored_points = self.board.compute_score(move)
        self.history[self.turn] = new_words
        self.players[self.curr_player].score += scored_points
        self.board.add_tiles(move)

        if not self.get_curr_rack():
            self.end_game()

        self.pass_turn()

    def __get_print_scores(self):
        scores = [self.players[pl_id].score for pl_id in self.pl_ids]
        print('Scores:')
        print(*zip(self.pl_ids, scores))
        return scores

    def pass_turn(self):
        self.turn += 1
        self.curr_player = self.get_curr_player()

    def exchange_tiles(self, tiles):
        temp_rack = deepcopy(self.get_curr_rack())
        for tile in tiles:
            try:
                temp_rack.remove(tile)
            except ValueError as err:
                raise NotInRack from err
        rack = self.get_curr_rack()
        for tile in tiles:
            rack.remove(tile)
            self.purse.tiles.append(tile)
        self.purse.shuffle()
        rack.extend(self.purse.draw(len(tiles)))
        self.pass_turn()

    def display_info(self) -> None:
        print(f'Turn: {self.turn}')
        print(f'Tiles in purse: {len(self.purse)}')
        self.__get_print_scores()
        print(self.board)
        print(f'Player turn: {self.curr_player}')
        print(self.get_curr_rack())

    def check_format_move(self, move):
        move_letters = move.values()
        temp_rack = deepcopy(self.get_curr_rack())
        for letter in move_letters:
            try:
                temp_rack.remove(Tile(letter))
            except ValueError as err:
                raise NotInRack from err
        return [Tile(move[pos], pos) for pos in move.keys()]

    def update_rack(self, move):
        letters = move.values()
        rack = self.get_curr_rack()
        for letter in letters:
            rack.remove(Tile(letter))
            try:
                rack.extend(self.purse.draw())
            except EmptyPurse:
                print('No more tile in purse')

    def end_game(self):
        print(f'Game is finished by {self.curr_player}')
        racks = [self.players[pl_id].rack for pl_id in self.players]
        remaining_tiles = sum(racks, [])
        print(remaining_tiles)
        bonus_points = sum(tile.value for tile in remaining_tiles)
        print(f'Finihser {self.curr_player} get {bonus_points} bonus_points by emptying his rack')
        self.players[self.curr_player].score += bonus_points

        final_scores = self.__get_print_scores()
        winner_idx = final_scores.index(winner_score := max(final_scores))
        winner = self.pl_ids[winner_idx]
        print(f'Winner is {winner} with a score of {winner_score}')

    # move: {(x, y): letter}, dict(pos:str)
    def submit(self, move) -> None:
        try:
            print('move submission')
            move_formated = self.check_format_move(move)
            next_words = self.board.get_next_words(move_formated)
        except BadWords as err:
            print('BadWords Error:')
            print(f'These words are unvalid : {err.bad_words}')
            print(f'These words are valid: {err.good_words}')
        except ScrabbleError as err:
            print('Scrabble Error')
            print(f'Type: {type(err).__name__}')
            print(err.args)
        else:
            print(f'Added words: {next_words}')
            self.update_rack(move)
            self.save_move(move_formated)
        finally:
            self.display_info()

    def input_move(self):
        """
        Move input, format: x, y, letter
        """
        input_list = input('Enter move, format: x1,y1,letter1,x2,y2,letter2,...').rsplit(',')
        keyfunc = lambda l: l[:3]
        input_tiles = groupby(input_list, keyfunc)

    def cli_play(self):
        raise NotImplementedError
