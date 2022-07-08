from scrabble_python import Scrabble
from scrabble_python.errors import ScrabbleError
import pytest

custom_scrabble_config = {
    'board_size': 11,
    'rack_size': 5,
    'lang': 'en'
}


def test_default_config_scrabble_init():
    scrabble = Scrabble()
    assert scrabble.board_size == Scrabble.dft_board_size
    assert scrabble.rack_size == Scrabble.dft_rack_size
    assert scrabble.lang == Scrabble.dft_lang
    assert len(scrabble.players) == scrabble.nb_players == 2
    assert [len(player.rack) for player in scrabble.players] == [
        scrabble.rack_size] * scrabble.nb_players
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
    assert 'available languages' in str(excinfo.value)
