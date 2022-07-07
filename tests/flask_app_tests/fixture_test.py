from flask_app.db import get_mongo_db


def test_fixture_client(client):
    response = client.get('/hello')
    assert response.data == b'Automatic Waffle'


def test_app_fixture_creation_test_doc(app):
    with app.app_context():
        test_doc = get_mongo_db('test_coll').read_one_doc({'id': 'test_id'})
        assert test_doc['id'] == 'test_id'
        assert test_doc['test_key'] == 'test_value'
