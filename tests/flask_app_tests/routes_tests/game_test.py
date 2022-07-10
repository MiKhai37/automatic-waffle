from scrabble_python import Scrabble

basic_config = {
    'name': 'game_name',
    'nb_players': 2,
    'creator_id': 'player_1'
}


def test_get_game(client):
    game_resp = client.get('/game/game_1')
    assert game_resp.status_code == 200
    game = game_resp.json
    assert game['creator_id'] == 'player_1'


def test_post_default(client):
    post_game_resp = client.post('/game/', json=basic_config)
    assert post_game_resp.status_code == 201
    game_id = post_game_resp.json['id']
    get_game_resp = client.get(f'/game/{game_id}')
    game_doc = get_game_resp.json
    assert game_doc['creator_id'] == basic_config['creator_id']
    assert game_doc['players'] == [{'id': 'player_1', 'pseudo': 'pseudo_1'}]
    assert game_doc['config']['board_size'] == Scrabble.df_board_size
    assert game_doc['config']['rack_size'] == Scrabble.df_rack_size
    assert game_doc['state'] == 'unstarted'


def test_post_custom_config(client):
    post_game_resp = client.post(
        '/game/', json=basic_config | {'board_size': 10, 'rack_size': 5}
    )
    assert post_game_resp.status_code == 201
    game_id = post_game_resp.json['id']
    get_game_resp = client.get(f'/game/{game_id}')
    game_doc = get_game_resp.json
    assert game_doc['config']['board_size'] == 10
    assert game_doc['config']['rack_size'] == 5


def test_join_game(client):
    join_resp = client.put(
        '/game/join',
        json={'player_id': 'player_2', 'game_id': 'game_1'}
    )
    assert join_resp.status_code == 201
    get_game_resp = client.get('/game/game_1')
    game_doc = get_game_resp.json
    players = game_doc['players']
    player_ids = {player['id'] for player in players}
    assert len(players) == 2
    assert player_ids == {'player_1', 'player_2'}
    # test duplicate joins
    client.put(
        '/game/join',
        json={'player_id': 'player_2', 'game_id': 'game_1'}
    )
    get_game_resp = client.get('/game/game_1')
    game_doc = get_game_resp.json
    players = game_doc['players']
    player_ids = {player['id'] for player in players}
    assert len(players) == 2
    assert player_ids == {'player_1', 'player_2'}


def test_join_full_game(client):
    join_full_resp = client.put(
        '/game/join', json={'player_id': 'player_1', 'game_id': 'game_full'})
    assert join_full_resp.status_code == 403
    assert join_full_resp.json['err_msg'] == 'game is complete'


def test_leave_game(client):
    leave_resp = client.put(
        '/game/leave', json={'player_id': 'player_2', 'game_id': 'game_1'})
    assert leave_resp.status_code == 201
    get_game_resp = client.get('/game/game_1')
    game_doc = get_game_resp.json
    players = game_doc['players']
    player_ids = {player['id'] for player in players}
    assert len(players) == 1
    assert 'player_2' not in player_ids


def test_creator_leave_game(client):
    creator_leave_resp = client.put(
        '/game/leave', json={'player_id': 'player_2', 'game_id': 'game__creator_leave'})
    assert creator_leave_resp.status_code == 403
    assert creator_leave_resp.json['err_msg'] == 'creator cannot leave'


def test_start_game(client):
    start_resp = client.put('/game/start', json={'game_id': 'game_1', 'creator_id': 'player_1'})
    assert start_resp.status_code == 201
    game_resp = client.get('/game/game_1')
    assert game_resp.json['state'] == 'running'


def test_start_uncomplete_game(client):
    start_resp = client.put('/game/start', json={'game_id': 'game_1', 'creator_id': 'player_1'})
    assert start_resp.status_code == 403
    assert start_resp.json['err_msg'] == 'uncomplete game'


def test_delete_game(client):
    del_resp = client.delete('/game/game_1')
    assert del_resp.status_code == 204
    dup_del_resp = client.get('/game/game_1')
    assert dup_del_resp.status_code == 404
