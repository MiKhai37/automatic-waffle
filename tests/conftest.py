import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pymongo import InsertOne, MongoClient
from scrabble_flask import create_app
from scrabble_python import Scrabble
from scrabble_python.items import Player
from scrabble_python.items.purse import Purse
from scrabble_python.items.tile import Tile


@pytest.fixture(scope='session')
def app() -> Flask:
    """
    Create an app fixture for testing, which use a specific testing database
    """
    app = create_app({'TESTING': True, 'DB_NAME': 'Testing'})
    populate_test_db()
    return app


@pytest.fixture(scope='session')
def client(app: Flask) -> FlaskClient:
    """
    Create a test client to remplace the browser during test
    """
    return app.test_client()


def populate_test_db() -> None:
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


@pytest.fixture(scope='session')
def scrabble_game() -> Scrabble:
    """
    Create a scrabble game fixture for testing purpose
    """
    player1 = Player('player_1')
    player2 = Player('player_2')
    players = [player1, player2]
    scrabble_config = {
        'board_size': 15,
        'rack_size': 7,
        'lang': 'fr'
    }
    return Scrabble(players, scrabble_config)


@pytest.fixture(scope='session')
def fake_purse() -> Purse:
    tiles = [
        Tile(),
        Tile(),
    ]
    return Purse(tiles, 'fr')
