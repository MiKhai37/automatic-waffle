from scrabble_python import Scrabble
from scrabble_python.errors import ScrabbleError
import pytest

from scrabble_python.items.player import Player

custom_scrabble_config = {
    'board_size': 11,
    'rack_size': 5,
    'lang': 'fr'
}

player1 = Player('player1')
player2 = Player('player2')
player3 = Player('player3')
player4 = Player('player4')


def test_config_scrabble_init():
    def_scrabble = Scrabble()
    assert def_scrabble.config['BOARD_SIZE'] == Scrabble.df_board_size
    assert def_scrabble.config['RACK_SIZE'] == Scrabble.df_rack_size
    assert def_scrabble.config['LANG'] == Scrabble.df_lang
    assert len(def_scrabble.players) == def_scrabble.nb_players == 2
    assert all(len(def_scrabble.players[player_id].rack) == def_scrabble.config['RACK_SIZE'] for player_id in def_scrabble.players)
    assert len(def_scrabble.purse) == 102 - \
        (def_scrabble.config['RACK_SIZE']*def_scrabble.nb_players)
    cust_scrabble = Scrabble(**custom_scrabble_config)
    assert cust_scrabble.config['BOARD_SIZE'] == custom_scrabble_config['board_size']
    assert cust_scrabble.config['RACK_SIZE'] == custom_scrabble_config['rack_size']
    assert cust_scrabble.config['LANG'] == custom_scrabble_config['lang']
    print([cust_scrabble.players[player_id].rack for player_id in cust_scrabble.players])
    assert all(len(cust_scrabble.players[player_id].rack) == cust_scrabble.config['RACK_SIZE'] for player_id in cust_scrabble.players)
    assert len(cust_scrabble.purse) == 102 - \
        (cust_scrabble.config['RACK_SIZE']*cust_scrabble.nb_players)


def test_unvalid_lang():
    with pytest.raises(ScrabbleError) as excinfo:
        Scrabble(lang='jklhsqd')
    assert 'jklhsqd' in str(excinfo.value)

def test_submit(test_scrabble):
    pass
