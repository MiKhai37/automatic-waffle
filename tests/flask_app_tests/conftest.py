from flask import Flask
import pytest
from flask_app import create_app
from flask_app.db import get_mongo_db


@pytest.fixture
def app():
    """
    Create an app fixture for testing, which use a specific testing database
    """
    app = create_app({'TESTING': True, 'DB_NAME': 'Testing', })

    # Initialization of testing documents
    with app.app_context():
        get_mongo_db('test_coll').insert_doc(
            {'id': 'test_id', 'test_key': 'test_value'})

    yield app

    # Deletion of testing documents
    with app.app_context():
        get_mongo_db('test_coll').delete_doc({'id': 'test_id'})


@pytest.fixture
def client(app: Flask):
    """
    Create a test client to remplace the browser during test
    """
    return app.test_client()
