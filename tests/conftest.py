import os
from itertools import chain

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pymongo import InsertOne, MongoClient
from scrabble_flask import create_app
from scrabble_python import Scrabble
from scrabble_python.items import Board, Player, Purse, Tile


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
def app() -> Flask:
    """
    Create an app fixture for testing, which use a specific testing database
    """
    populate_test_db()
    return create_app({'TESTING': True, 'DB_NAME': 'Testing'})


@pytest.fixture(scope='session')
def client(app: Flask) -> FlaskClient:
    """
    Create a test client to remplace the browser during test
    """
    return app.test_client()


@pytest.fixture(scope='session')
def test_scrabble() -> Scrabble:
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
    return Scrabble(players = players, **scrabble_config)


@pytest.fixture(scope='session')
def fake_purse() -> Purse:
    p1_letters = ['M', 'A', 'I', 'S', 'O', 'N']
    p2_letters = ['O', 'U', 'P', 'E']
    p1_tiles = [Tile(letter) for letter in p1_letters]
    p2_tiles = [Tile(letter) for letter in p2_letters]
    purse_tile = list(chain.from_iterable(zip(p1_tiles, p2_tiles)))
    return Purse(purse_tile, 'fr')


@pytest.fixture(scope='session')
def empty_test_board() -> Board:
    """An empty test board"""
    return Board()


@pytest.fixture(scope='function')
def test_board():
    """A test board with the word test placed in the center"""
    first_tiles = [Tile('T', (7, 7)), Tile('E', (7, 8)),
                   Tile('S', (7, 9)), Tile('T', (7, 10))]
    return Board(first_tiles)
