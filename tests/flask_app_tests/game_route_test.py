from scrabble_python import Scrabble

basic_config = {
    'name': 'game_name',
    'nb_players': 2,
    'player_id': 'player_id_1'
}


def test_default_config_post_game(client):
    post_game_response = client.post('/game/', json=basic_config)
    assert post_game_response.status_code == 201

    game_id = post_game_response.json['id']
    get_game_response = client.get(f'/game/{game_id}')
    game_infos = get_game_response.json
    assert game_infos['creator_id'] == basic_config['player_id']
    assert game_infos['players'] == [{'pseudo': 'player_1'}]
    assert game_infos['board_size'] == Scrabble.default_board_size
    assert game_infos['rack_size'] == Scrabble.default_rack_size


def test_custom_config_post_game(client):
    post_game_response = client.post(
        '/game/', json=basic_config.update({'board_size': 10, 'rack_size': 5})
    )
    assert post_game_response.status_code == 201
    game_id = post_game_response.json['id']
    get_game_response = client.get(f'/game/{game_id}')
    game_infos = get_game_response.json
    assert game_infos['board_size'] == 15
    assert game_infos['rack_size'] == 7


def test_join_game(client):
    pass


def test_start_game(client):
    pass
