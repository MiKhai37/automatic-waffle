import os
from flask_app import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
    assert create_app().config['DB_NAME'] == os.getenv('DB_NAME')
    assert create_app({'DB_NAME': 'truc'}).config['DB_NAME'] == 'truc'
