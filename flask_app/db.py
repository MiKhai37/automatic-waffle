from flask import Flask, current_app, g

from .mongo_api import MongoAPI


def get_mongo_db(collection: str):
    current_app.logger.debug(f'MONGODB {collection} Opened')
    if 'mongo_db' not in g:
        g.mongo_db = MongoAPI(
            collection=collection,
            uri=current_app.config['MONGO_URI'],
            db_name=current_app.config['DB_NAME']
        )

    return g.mongo_db


def close_mongo_db(e=None):
    mongo_db = g.pop('mongo_db', None)
    if mongo_db is not None:
        current_app.logger.debug('MONGODB Closed')
        mongo_db.close_db()


def link_app(app: Flask):
    app.logger.debug('MONGODB Linked')
    app.teardown_appcontext(close_mongo_db)
