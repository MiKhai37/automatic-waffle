def test_get_player(client):
    player_resp = client.get('/player/player_1')
    assert player_resp.status_code == 200


def test_post_player(client):
    test_player_pseudo = 'test_pseudo'
    post_resp = client.post(
        '/player/',
        json={'pseudo': test_player_pseudo}
    )
    assert post_resp.status_code == 201
    new_player_id = post_resp.json['id']
    get_resp = client.get(f'/player/{new_player_id}')
    assert get_resp.json['id'] == new_player_id
    assert get_resp.json['pseudo'] == test_player_pseudo


def test_get_players(client):
    players_resp = client.get('/player/')
    assert players_resp.status_code == 200
    print(players_resp.json)
    assert len(players_resp.json) == 3


def test_delete_player(client):
    del_resp = client.delete('/player/player_1')
    assert del_resp.status_code == 204
    get_resp = client.get('/player/player_1')
    assert get_resp.status_code == 404


def test_delete_404(client):
    redelete_resp = client.delete('/player/unexistent_id')
    assert redelete_resp.status_code == 404
