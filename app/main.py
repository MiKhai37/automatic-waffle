import logging
from flask import Flask, request, json, Response
from flask_cors import CORS, cross_origin
from MongoAPI import MongoAPI
import uuid

app = Flask(__name__)
CORS(app, support_credentials=True)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

"""
Routes Summary
- /
Return backend status

-/games/all
Return all game documents

-/games/get
Return game document correspondig to the given game ID

-/games/info/all
Return all game info documents

-/games/info/get
Return game info correspondig to the given game ID

-/games/create
Create a game document

-/games/update
Update the game document correspondig to the given game ID

-/games/delete
Delete the game document correspondig to the given game ID
"""

@app.route('/')
@cross_origin(supports_credentials=True)
def base():
  app.logger.debug('This is a DEBUG log record.')
  app.logger.info('This is an INFO log record.')
  app.logger.warning('This is a WARNING log record.')
  app.logger.error('This is an ERROR log record.')
  app.logger.critical('This is a CRITICAL log record.')
  return Response(response=json.dumps({"Status": "UP"}),
                  status=200,
                  mimetype='application/json')

@app.route('/games/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllGames():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    app.logger.warning('MongoDB read all games: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.read()
  app.logger.info('MongoDB read all games: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readOneGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    app.logger.warning('MongoDB read game: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readOne()
  app.logger.info('MongoDB read game: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/info/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllGameInfo():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    app.logger.warning('MongoDB read all info games: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readAllGameInfo()
  app.logger.info('MongoDB read all info games: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/info/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readOneGameInfo():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    app.logger.warning('MongoDB read info game: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readOneGameInfo()
  app.logger.info('MongoDB read info game: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

initialTiles = [
  {'letter': 'A', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 0}},
  {'letter': 'B', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 1}},
  {'letter': 'C', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 2}},
  {'letter': 'D', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 3}},
  {'letter': 'E', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 4}},
  {'letter': 'F', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 5}},
  {'letter': 'G', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 6}}
];

@app.route('/games/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_createGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {} or 'Document' not in data:
    app.logger.warning('MongoDB create game: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)

  data['Document']['tiles'] = initialTiles

  data['Document']['gameInfo'] = {'gameID': data['Document']['gameID'], 'gameName': data['Document']['gamename'], 'nbPlayers': data['Document']['nbPlayers'], 'state': 'waiting'}

  nbPlayers = int(data['Document']['nbPlayers'])
  data['Document']['players'] = [f'Joueur  {i + 1}' for i in range(nbPlayers)]
  data['Document']['devPlayers'] = [{'pseudo': f'Joueur  {i + 1}', 'tiles': initialTiles} for i in range(nbPlayers)]

  response = obj1.write(data)
  app.logger.info('MongoDB create game: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/update', methods=['PUT'])
@cross_origin(supports_credentials=True)
def mongo_updateGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {} or 'DataToBeUpdated' not in data:
    app.logger.warning('MongoDB update game: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.update()
  app.logger.info('MongoDB update game: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/delete', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def mongo_deleteGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {} or 'Filter' not in data:
    app.logger.warning('MongoDB delete game: fail, no data provided')
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.delete(data)
  app.logger.info('MongoDB delete game: success')
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')
