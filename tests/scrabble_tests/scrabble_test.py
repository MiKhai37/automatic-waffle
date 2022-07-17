from scrabble_python import Scrabble
from scrabble_python.errors import ScrabbleError
import pytest

from scrabble_python.items.player import Player

custom_config = {
    'board_size': 11,
    'rack_size': 5,
    'lang': 'fr'
}

player1 = Player('player1')
player2 = Player('player2')
player3 = Player('player3')
player4 = Player('player4')


def test_config_scrabble_init():
    def_game = Scrabble()
    assert def_game.config['BOARD_SIZE'] == Scrabble.df_bsize
    assert def_game.config['RACK_SIZE'] == Scrabble.df_rsize
    assert def_game.config['LANG'] == Scrabble.df_lang
    assert len(def_game.players) == def_game.nb_plys == 2
    assert all(len(def_game.players[pl_id].rack) ==
               def_game.config['RACK_SIZE'] for pl_id in def_game.players)
    assert len(def_game.purse) == 102 - \
        (def_game.config['RACK_SIZE']*def_game.nb_plys)
    cust_game = Scrabble(**custom_config)
    assert cust_game.config['BOARD_SIZE'] == custom_config['board_size']
    assert cust_game.config['RACK_SIZE'] == custom_config['rack_size']
    assert cust_game.config['LANG'] == custom_config['lang']
    print([cust_game.players[player_id].rack for player_id in cust_game.players])
    assert all(len(cust_game.players[pl_id].rack) ==
               cust_game.config['RACK_SIZE'] for pl_id in cust_game.players)
    assert len(cust_game.purse) == 102 - \
        (cust_game.config['RACK_SIZE']*cust_game.nb_plys)


def test_unvalid_lang():
    with pytest.raises(ScrabbleError) as excinfo:
        Scrabble(lang='jklhsqd')
    assert 'jklhsqd' in str(excinfo.value)


@pytest.mark.parametrize('nb_tiles', [1, 2, 3, 4, 5, 6, 7])
def test_exchange_letter(nb_tiles):
    game = Scrabble()
    pl_id = game.get_curr_player()
    prev_dist = game.purse.get_dist()
    prev_len = len(game.purse)
    prev_rack = game.get_curr_rack().copy()
    to_exchange, to_keep = prev_rack[:nb_tiles], prev_rack[nb_tiles:]
    game.exchange_tiles(to_exchange)
    curr_dist = game.purse.get_dist()
    curr_len = len(game.purse)
    curr_rack = game.players[pl_id].rack
    assert prev_dist != curr_dist
    assert prev_len == curr_len
    assert prev_rack != curr_rack
    assert all(tile in curr_rack for tile in to_keep)
    # Not always true due to randomness
    #assert any(tile not in curr_rack for tile in tiles_to_exchange)
