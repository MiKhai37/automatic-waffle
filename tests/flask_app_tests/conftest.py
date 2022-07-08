import os
from flask import Flask
from pymongo import MongoClient
import pytest
from flask_app import create_app
from flask_app.db import get_mongo_db


@pytest.fixture
def app():
    """
    Create an app fixture for testing, which use a specific testing database
    """
    app = create_app({'TESTING': True, 'DB_NAME': 'Testing', })
    populate_test_db()
    yield app


@pytest.fixture
def client(app: Flask):
    """
    Create a test client to remplace the browser during test
    """
    return app.test_client()

def populate_test_db():
    admin_uri = os.getenv('MONGO_ADMIN_URI')
    admin_client = MongoClient(admin_uri)
    admin_client.drop_database('Testing')
    test_cursor = admin_client['Testing']
    player_coll = test_cursor['players']
    game_coll = test_cursor['games']
    player_coll.insert_one({'id': 'player_1', 'pseudo': 'pseudo_1'})
    player_coll.insert_one({'id': 'player_2', 'pseudo': 'pseudo_2'})
    game_coll.insert_one({
        'id': 'game_1',
        'creator_id': 'player_1',
        'name': 'name_1',
        'players': [{'id': 'player_1', 'pseudo': 'pseudo_1'}]}
    )

def drop_test_db():
    admin_uri = os.getenv('MONGO_ADMIN_URI')
    admin_client = MongoClient(admin_uri)
    admin_client.drop_database('Testing')
