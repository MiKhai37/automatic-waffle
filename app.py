import imp
from flask import Flask, message_flashed, render_template, session, request, \
    copy_current_request_context, json, Response
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_cors import CORS, cross_origin
from MongoAPI import MongoAPI
import uuid
from threading import Lock
import logging
from datetime import datetime

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, support_credentials=True)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=['http://localhost:3000', 'http://0.0.0.0:5000', 'https://friendly-funicular.vercel.app'])
thread = None
thread_lock = Lock()

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

#@app.route('/')
#@cross_origin(supports_credentials=True)
#def base():
#  return Response(response=json.dumps({"Status": "UP"}),
#                  status=200,
#                  mimetype='application/json')

@app.route('/games/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllGames():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readAll()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readOne()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/info/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllGameInfo():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readAllGameInfo()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/info/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readOneGameInfo():
  data = request.json
  data['collection']='games'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readOneGameInfo()
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
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/update', methods=['PUT'])
@cross_origin(supports_credentials=True)
def mongo_updateGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {} or 'DataToBeUpdated' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.update()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/delete', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def mongo_deleteGame():
  data = request.json
  data['collection']='games'

  if data is None or data == {} or 'Filter' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.delete(data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/users/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllUsers():
  data = request.json
  data['collection']='users'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readAllUsers()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/users/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readUser():
  data = request.json
  data['collection']='user'

  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.readUser()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/users/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_createUser():
  data = request.json
  data['collection']='users'

  if data is None or data == {} or 'Document' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')

  obj1 = MongoAPI(data)
  response = obj1.write(data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')
### SocketIO

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})


@app.route('/')
@cross_origin(supports_credentials=True)
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/test')
@cross_origin(supports_credentials=True)
def test():
    return render_template('test.html', async_mode=socketio.async_mode)

@socketio.event
def my_event(message):
    app.logger.info('my_event:' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'time': str(datetime.now()), 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    app.logger.info('my_broadcast_event:' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'time': str(datetime.now()), 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    app.logger.info('join:' + json.dumps(message))
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    app.logger.info('leave:' + json.dumps(message))
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])

@socketio.event
def what_are_my_rooms():
    emit('my_rooms', {'data': 'In rooms: ' + ', '.join(rooms())})


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('connect')
def test_connection():
    app.logger.info('Client connected: ' + request.sid)

@socketio.on('disconnect')
def test_disconnect():
    app.logger.info('Client disconnected: ' + request.sid)

if __name__ == '__main__':
    socketio.run(app)
