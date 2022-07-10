import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from scrabble_flask import create_app
from pymongo import InsertOne, MongoClient


@pytest.fixture(scope='session')
def app() -> Flask:
    """
    Create an app fixture for testing, which use a specific testing database
    """
    app = create_app({'TESTING': True, 'DB_NAME': 'Testing'})
    populate_test_db()
    yield app


@pytest.fixture(scope='session')
def client(app: Flask) -> FlaskClient:
    """
    Create a test client to remplace the browser during test
    """
    return app.test_client()


def populate_test_db():
    admin_uri = os.getenv('MONGO_ADMIN_URI')
    admin_client = MongoClient(admin_uri)
    admin_client.drop_database('Testing')
    test_database = admin_client.get_database('Testing')

    player_coll = test_database.get_collection('players')
    player_coll.bulk_write([
        InsertOne({'id': 'player_1', 'pseudo': 'pseudo_1'}),
        InsertOne({'id': 'player_2', 'pseudo': 'pseudo_2'}),
    ])

    game_coll = test_database.get_collection('games')
    game_coll.bulk_write([
        InsertOne({
            'id': 'game_1',
            'creator_id': 'player_1',
            'name': 'name_1',
            'players': [{'id': 'player_1', 'pseudo': 'pseudo_1'}]
        })
    ])
