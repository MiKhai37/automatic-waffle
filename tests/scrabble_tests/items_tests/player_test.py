from scrabble_python import Player, Tile


def test_init_player():
    player = Player()
    assert player.score == 0
    assert player.rack == []


def test_player():
    player = Player(player_id='id_str', score=5, rack=[Tile('A'), Tile('B')])
    assert player.ID == 'id_str'
    assert player.score == 5
    assert len(player.rack) == 2
