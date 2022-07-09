def test_get_all_players(client):
    post_response = client.get('/player/')
    assert post_response.status_code == 200
    print(post_response.json)
    assert len(post_response.json) == 2


def test_post_get_delete_player(client):
    test_player_pseudo = 'test_pseudo'
    post_response = client.post(
        '/player/', json={'pseudo': test_player_pseudo}
    )
    assert post_response.status_code == 201
    new_player_id = post_response.json['id']
    get_response = client.get(f'/player/{new_player_id}')
    assert get_response.json['id'] == new_player_id
    assert get_response.json['pseudo'] == test_player_pseudo

    delete_response = client.delete(f'/player/{new_player_id}')
    assert delete_response.status_code == 201

    reget_response = client.get(f'/player/{new_player_id}')
    assert reget_response.status_code == 404


def test_post_unvalid_body(client):
    post_uncomplete_body_response = client.post(
        '/player/', json={'pseudio': 'test_pseudo'})
    assert post_uncomplete_body_response.status_code == 400


def test_post_too_much_body(client):
    post_to_much_body_response = client.post(
        '/player/', json={'pseudo': 'test_pseudo', 'too_pseudo': 'test_too_pseudo'})
    assert post_to_much_body_response.status_code == 400


def test_delete_404(client):
    redelete_response = client.delete('/player/unexistent_id')
    assert redelete_response.status_code == 404
