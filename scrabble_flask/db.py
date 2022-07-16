from flask import Flask, current_app, g

from scrabble_flask.mongo_api import MongoAPI


def get_mongo_db(collection: str) -> MongoAPI:
    if f'{collection}_db' not in g:
        current_app.logger.debug(f'MONGODB {collection} Opened')
        g.setdefault(f'{collection}_db', MongoAPI(
            collection=collection,
            uri=current_app.config['MONGO_URI'],
            db_name=current_app.config['DB_NAME']
        ))
        
    return g.get(f'{collection}_db')

# TODO fix close the connection
def close_mongo_db(e=None):
    coll_names = ['players_db', 'games_db', 'plays_db']
    mongo_colls = [g.pop(coll_name, None) for coll_name in coll_names]
    for mongo in [mongo for mongo in mongo_colls if mongo is not None]:
        current_app.logger.debug(f'MONGODB {mongo.collection.name} Closed')
        mongo.close_db()


def link_app(app: Flask):
    app.logger.debug('MONGODB Linked')
    app.teardown_appcontext(close_mongo_db)
