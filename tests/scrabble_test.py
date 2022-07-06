from scrabble_python import Scrabble

scrabble_config = {
    'board_size': 15,
    'rack_size': 7,
    'lang': 'fr'
}


def test_scrabble_init():
    scrabble = Scrabble(**scrabble_config)
    assert len(scrabble.players) == scrabble.nb_players == 2
    assert [len(player.rack) for player in scrabble.players] == [scrabble.rack_size] * scrabble.nb_players
    assert len(scrabble.purse) == 102 - (scrabble.rack_size*scrabble.nb_players)
    assert not scrabble.purse_is_empty
