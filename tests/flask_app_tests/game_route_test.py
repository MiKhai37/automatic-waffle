from scrabble_python import Scrabble

basic_config = {
    'name': 'game_name',
    'nb_players': 2,
    'creator_id': 'player_1'
}


def test_get_game(client):
    get_game_resp = client.get('/game/game_1')
    assert get_game_resp.status_code == 200
    game = get_game_resp.json
    assert game['creator_id'] == 'player_1'


def test_default_config(client):
    post_game_response = client.post('/game/', json=basic_config)
    assert post_game_response.status_code == 201

    game_id = post_game_response.json['id']
    print(game_id)
    get_game_response = client.get(f'/game/{game_id}')
    game_doc = get_game_response.json
    print(get_game_response)
    print(game_doc)
    assert game_doc['creator_id'] == basic_config['creator_id']
    assert game_doc['players'] == [{'id': 'player_1', 'pseudo': 'pseudo_1'}]
    assert game_doc['config']['board_size'] == Scrabble.dft_board_size
    assert game_doc['config']['rack_size'] == Scrabble.dft_rack_size


def test_custom_config(client):
    post_game_response = client.post(
        '/game/', json=basic_config|{'board_size': 10, 'rack_size': 5}
    )
    assert post_game_response.status_code == 201
    game_id = post_game_response.json['id']
    get_game_response = client.get(f'/game/{game_id}')
    game_doc = get_game_response.json
    assert game_doc['config']['board_size'] == 10
    assert game_doc['config']['rack_size'] == 5




def test_join_game(client):
    join_resp = client.post('/game/join', json={'player_id': 'player_2', 'game_id': 'game_1'})
    join_resp = client.post('/game/join', json={'player_id': 'player_2', 'game_id': 'game_1'})
    assert join_resp.status_code == 201
    get_game_resp = client.get('/game/game_1')
    game_doc = get_game_resp.json
    players = game_doc['players']
    player_ids = {player['id'] for player in players}
    assert len(players) == 2
    assert player_ids == {'player_1', 'player_2'}

def test_leave_game(client):
    pass
