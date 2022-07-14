from scrabble_python import Scrabble
from scrabble_python.errors import ScrabbleError
import pytest

from scrabble_python.items.player import Player

custom_scrabble_config = {
    'board_size': 11,
    'rack_size': 5,
    'lang': 'en'
}

player1 = Player('player1')
player2 = Player('player2')
player3 = Player('player3')
player4 = Player('player4')


def test_default_config_scrabble_init():
    scrabble = Scrabble()
    assert scrabble.board_size == Scrabble.df_board_size
    assert scrabble.rack_size == Scrabble.df_rack_size
    assert scrabble.lang == Scrabble.df_lang
    assert len(scrabble.players) == scrabble.nb_players == 2
    assert all(len(scrabble.players[player_id].rack) == scrabble.rack_size for player_id in scrabble.players)
    assert len(scrabble.purse) == 102 - \
        (scrabble.rack_size*scrabble.nb_players)
    assert not scrabble.purse_is_empty


def test_custom_config_scrabble_init():
    scrabble = Scrabble(**custom_scrabble_config)
    assert scrabble.board_size == custom_scrabble_config['board_size']
    assert scrabble.rack_size == custom_scrabble_config['rack_size']
    assert scrabble.lang == custom_scrabble_config['lang']


def test_unvalid_lang():
    with pytest.raises(ScrabbleError) as excinfo:
        scrabble = Scrabble(lang='jklhsqd')
    assert 'jklhsqd' in str(excinfo.value)

def test_submit(scrabble_game):
    pass
