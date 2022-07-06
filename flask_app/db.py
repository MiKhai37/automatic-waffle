from flask import Flask, g

from .mongo_api import MongoAPI

def get_mongo_db(collection: str):
    if 'mongo_db' not in g:
        g.mongo_db = MongoAPI(collection)

    return g.mongo_db

def close_mongo_db():
    mongo_db = g.pop('mongo_db', None)
    if mongo_db is not None:
        mongo_db.close_db()

def link_app(app: Flask):
    app.logger.debug('MONGODB Link Initialization')
    app.teardown_appcontext(close_mongo_db)