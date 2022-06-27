from flask import Flask, make_response, render_template, session, request, \
    copy_current_request_context, json, Response
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_cors import CORS, cross_origin
# from flask_session import Session
from MongoAPI import MongoAPI
import uuid
from threading import Lock
import logging
from datetime import datetime
import string
import random

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_very_secret!'
CORS(app, support_credentials=True)

# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SESSION_COOKIE_NAME'] = 'flask-cookie'
# app.config['SESSION_MONGODB'] = MongoAPI('session').client
# Session(app)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
thread = None
thread_lock = Lock()

# TODO: manage login, and logged user
# games played, games won, game lost,
# highiest score, messages, challenge other user...)


@app.before_request
def hook():
    # Middleware invoke before each request
    app.logger.info(f"Request Info: endpoint: {request.method} \
        {request.endpoint}, url: {request.path}, path: {request.path}")


@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def index():
    """Get backend server status"""
    app.logger.info('GET 200 /index')
    session['key'] = 'value'
    return render_template('index.html')


@app.route('/setcookie')
@cross_origin(supports_credentials=True)
def setCookie():
    resp = make_response('The cookie has been set')
    resp.set_cookie('TestCookie', 'TestValue')
    return resp


@app.route('/player', methods=['GET'])
@cross_origin(supports_credentials=True)
def getPlayers():
    """Get all players documents"""
    playersApi = MongoAPI('players')
    playerDocs = playersApi.readMany()

    app.logger.info(f"GET 200 /players, count: {len(playerDocs)}")
    return Response(response=json.dumps(playerDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/player', methods=['POST'])
@cross_origin(supports_credentials=True)
def postPlayer():
    """Create a new player, by inserting a new document in players collection"""
    reqProps = ['pseudo']
    newDoc = request.json

    if not all (prop in newDoc for prop in reqProps):
        app.logger.error(f"POST 404 /player, Missing properties, {reqProps}")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Required property(ies) in body request is(are) missing' ,'reqProps': reqProps}),
                        status=400,
                        mimetype='application/json')

    newDoc['id'] = str(uuid.uuid4())

    playersApi = MongoAPI('players')
    playerDoc = playersApi.create(newDoc)

    app.logger.info(f"POST 201 /player,New Document Successfully Inserted, ID: {playerDoc['id']}")
    return Response(response=json.dumps(playerDoc),
                  status=201,
                  mimetype='application/json')


@app.route('/player/<playerID>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def getOrDeletePlayer(playerID):
    """
    /player/<playerID> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding player document
    - DELETE endpoint

        Delete the corresponding player document
    """
    playersApi = MongoAPI('players')

    if request.method == 'GET':
        playerDoc = playersApi.readOne({'id': playerID})

        if (playerDoc.get('Code') == 404):
            app.logger.error(f"GET 404 /player/{playerID}, This player doesn't exist")
            return Response(response=json.dumps({'err': True, 'errMsg': "This player doesn't exist"}),
                        status=404,
                        mimetype='application/json')

        app.logger.info(f"GET 200 /player/{playerID}, pseudo: {playerDoc['pseudo']}")
        return Response(response=json.dumps(playerDoc),
                        status=200,
                        mimetype='application/json')


    if request.method == 'DELETE':
        if ('Test' in playerID):
            app.logger.error(f"DELETE 403 /player/{playerID}, It's a test document, its deletion is unallowed")
            return Response(response=json.dumps({'err': True, 'errMsg': "It's a test document, its deletion is unallowed"}),
                            status=403,
                             mimetype='application/json')

        deletePlayerResult = playersApi.delete({'id': playerID})

        app.logger.info(f"DELETE {deletePlayerResult['Code']} /player/{playerID}, Player {deletePlayerResult['Status']}")
        return Response(response=json.dumps(deletePlayerResult),
                        status=deletePlayerResult['Code'],
                        mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first
@app.route('/player/join', methods=['PUT'])
@cross_origin(supports_credentials=True)
def playerJoin():
    """Add a player to the game, by adding it to its gameInfo document"""
    playerID = request.json['playerID']
    gameID = request.json['gameID']

    playersApi = MongoAPI('players')
    infosApi = MongoAPI('infos')

    playerDoc = playersApi.readOne({'id': playerID})
    infoDoc = infosApi.readOne({'id': gameID})

    if (playerDoc.get('Code') == 404 or infoDoc.get('Code') == 404):
        app.logger.error(f"PUT 404 /player/join, Player or Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': "Player or Game not found"}),
                        status=404,
                        mimetype='application/json')


    nbPlayers = infoDoc['nbPlayers']
    players = infoDoc['players']
    playerIDs = map(lambda player: player['id'], players)

    if (playerID in playerIDs):
        app.logger.error(f"PUT 403 /player/join, Player already in game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player already in game'}),
            status=403,
            mimetype='application/json')

    if (len(players) >= nbPlayers):
        app.logger.error(f"PUT 403 /player/join, No place available")
        return Response(response=json.dumps({'err': True, 'errMsg': 'No place available'}),
                    status=403,
                    mimetype='application/json')

    players.append(playerDoc)
    updateResult = infosApi.update(filt={'id': gameID}, dataToBeUpdated={'players': players})
    app.logger.info(f"PUT 200 /player/join, Player {playerID} joins the game {gameID}")
    return Response(response=json.dumps(updateResult),
        status=200,
        mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first
@app.route('/player/leave', methods=['PUT'])
@cross_origin(supports_credentials=True)
def playerLeave():
    """Remove a player from the game, by removing it from its gameInfo document"""
    playerID = request.json['playerID']
    gameID = request.json['gameID']

    infosApi = MongoAPI('infos')
    infoDoc = infosApi.readOne({'id': gameID})
    
    if (infoDoc.get('Code') == 404):
        app.logger.error(f"PUT 404 /player/leave, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')


    players = infoDoc['players']
    playerIDs = map(lambda player: player['id'], players)
    
    if (playerID not in playerIDs):
        app.logger.error(f"PUT 404 /player/leave, Player not in game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in game'}),
            status=404,
            mimetype='application/json')

    player = list(filter(lambda player: (player['id'] == playerID), players))[0]
    # player = next(filter(lambda player: (player['id'] == playerID), players), None)
    # player = [player for player in players if player['id'] == playerID][0] # Or .pop() instead of [0]
    players.remove(player)
    updateInfoResult = infosApi.update(filt={'id': gameID}, dataToBeUpdated={'players': players})
    app.logger.info(f"PUT 200 /player/leave, Player {playerID} leaves the game {gameID}")
    return Response(response=json.dumps(updateInfoResult),
        status=200,
        mimetype='application/json')


### Games Routes and Endpoints ###
@app.route('/game', methods=['GET'])
@cross_origin(supports_credentials=True)
def getGames():
    """Get all infoGame documents"""
    infosApi = MongoAPI('infos')
    infoDocs = infosApi.readMany()

    app.logger.info(f'GET 200 /games, count: {len(infoDocs)}')
    return Response(response=json.dumps(infoDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/game', methods=['POST'])
@cross_origin(supports_credentials=True)
def postGame():
    """Create a new game, by inserting a new document in gameInfos collection"""
    newInfoDoc = request.json

    playersApi = MongoAPI('players')
    creatorPlayerDoc = playersApi.readOne({'id': newInfoDoc['creatorID']})
    if creatorPlayerDoc.get('Code') == 404:
        app.logger.error(f"POST 404 /game, Creator not found")
        return Response(response=json.dumps({'err': True, 'errMsg': "Creator not found"}),
                        status=404,
                        mimetype='application/json')


    newInfoDoc['id'] = str(uuid.uuid4())
    newInfoDoc['players'] = [creatorPlayerDoc]
    newInfoDoc['state'] = 'unstarted'
    newInfoDoc['tilesPerRack'] = 7
    newInfoDoc['gridSize'] = 15

    infosApi = MongoAPI('infos')
    gameInfo = infosApi.create(newInfoDoc)
    
    app.logger.info(f"POST 201 /game, New Document Successfully Inserted, ID: {newInfoDoc['id']}")
    return Response(response=json.dumps(gameInfo),
                    status=201,
                    mimetype='application/json')


@app.route('/game/<gameID>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def getOrDeleteGame(gameID):
    """
    # gameIdRoute
    ## /game/<gameID> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding gameInfo document
    - DELETE endpoint

        Delete the corresponding gameInfo document
    """
    infosApi = MongoAPI('infos')

    if request.method == 'GET':
        infoDoc = infosApi.readOne({'id': gameID}) 

        if (infoDoc.get('Code') == 404):
            app.logger.error(f"GET 404 /game/{gameID}, Game not found")
            return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

        app.logger.info(f"GET 200 /game/{gameID}, name: {infoDoc['name']}")
        return Response(response=json.dumps(infoDoc),
                        status=200,
                        mimetype='application/json')

    # TODO Also remove the gameTile document if game was started
    if request.method == 'DELETE':
        if ('Test' in gameID):
            app.logger.error(f"DELETE 403 /game/{gameID}, It's a test document, its deletion is unallowed")
            return Response(response=json.dumps({'err': True, 'errMsg': "It's a test document, its deletion is unallowed"}),
                        status=403,
                        mimetype='application/json')

        infosApi = MongoAPI('infos')
        deleteGameResult = infosApi.delete({'id': gameID})

        app.logger.info(f"DELETE {deleteGameResult['Code']} /game/{gameID}, Game {deleteGameResult['Status']}")
        return Response(response=json.dumps(deleteGameResult),
                        status=deleteGameResult['Code'],
                        mimetype='application/json')


# @app.route('/play/move', methods=['PUT'])
# @cross_origin(supports_credentials=True)
# def mongo_updateGame(gameID):
#     app.logger.info(f"PUT 200 /games/{gameID}")
#     data = request.json
#     data['collection']='games'
#     data['Filter'] = {'gameID': gameID}

#     obj1 = MongoAPI('tiles')
#     response = obj1.update()
#     return Response(response=json.dumps(response),
#                     status=200,
#                     mimetype='application/json')
def createPurse():
    purse = []
    return purse

def getInitialTiles(purse, nbTiles=7):
    # copy purse to avoid parms mutation, Clean Code
    purseCopy = purse.copy()
    tiles = [{'letter': random.choice(string.ascii_uppercase), 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': {'place': 'rack', 'coords': i}} for i in range(nbTiles)]
    return tiles, purseCopy


@app.route('/play/start', methods=['POST'])
@cross_origin(supports_credentials=True)
def startGame():
    """Start the game, by updating its infoGame document, and creating a gameTiles documents"""
    gameID = request.json['gameID']
    infosApi = MongoAPI('infos')
    infoDoc = infosApi.readOne({'id': gameID})
    if (infoDoc.get('Code') == 404):
        app.logger.error(f"POST 404 /play/start, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')


    # Avoid duplicate start operations
    if (infoDoc['state'] == 'running'):
        app.logger.error(f"POST 403 /play/start, Game is already running")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game is already running'}),
                        status=403,
                        mimetype='application/json')
    
    # TODO: implement override available places in frontend
    # overridePlace = request.json['overridePlace']
    overridePlace = False
    # Avoid game start with no required players
    if (len(infoDoc['players']) < infoDoc['nbPlayers'] and overridePlace is False):
        app.logger.error(f"POST 403 /play/start, Player(s) is(are) missing, {infoDoc['nbPlayers'] - len(infoDoc['players'])} place(s) available")
        return Response(response=json.dumps({'err': True, 'errMsg': f"Player(s) is(are) missing, {infoDoc['nbPlayers'] - len(infoDoc['players'])} place(s) available"}),
                        status=403,
                        mimetype='application/json')

    tilesApi = MongoAPI('tiles')


    # Updating the values of infoDoc
    # Note: The for loop mutates the player item of the players array in infoDoc
    for player in infoDoc['players']:
        player['score'] = 0

    infoDoc['turn'] = 0
    infoDoc['state'] = 'running'
    infoDoc['turnOffset'] = random.randint(0,len(infoDoc['players']))

    # Put the updated infoDoc to update
    infosApi.update({'id': gameID}, infoDoc)

    purse = createPurse()
    racks = []
    for player in infoDoc['players']:
        tiles, purse = getInitialTiles(purse, nbTiles=infoDoc['tilesPerRack'])
        racks.append({'playerID': player['id'], 'tiles': tiles})
    
    newTileDoc = {'gameID': gameID, 'board': [], 'racks': racks, 'purse': purse}

    # Post the new tileDoc
    gameTilesDoc = tilesApi.create(newTileDoc)

    app.logger.info(f"POST 201 /play/start, Game has been started")
    return Response(response=json.dumps(gameTilesDoc),
                    status=201,
                    mimetype='application/json')

@app.route('/play/giveup/', methods=['PUT'])
@cross_origin(supports_credentials=True)
def giveupGame():
    """Give up the game, by updating its infoGame document"""
    playerID = request.json['playerID']
    gameID = request.json['gameID']

    infosApi = MongoAPI('infos')
    tilesApi = MongoAPI('tiles')

    infoDoc = infosApi.readOne({'id': gameID})
    if (infoDoc.get('Code') == 404):
        app.logger.error(f"PUT 404 /play/giveup, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    # Avoid give up of unstarted game
    if (infoDoc['state'] == 'unstarted'):
        app.logger.error(f"PUT 403 /play/giveup, Game is not started, giveup is imppossible")
        return Response(response=json.dumps({'err': True, 'errMsg': ' Game is not started, giveup is impossible'}),
                        status=403,
                        mimetype='application/json')
    
    # Avoid duplicate give up
    if (infoDoc['state'] == 'finished'):
        app.logger.error(f"PUT 403 /play/giveup, Game is already finished")
        return Response(response=json.dumps({'err': True, 'errMsg': ' Game is already finished'}),
                        status=403,
                        mimetype='application/json')
    # TODO: select the highest score
    winner = "player with highest score"

    updateInfoDoc = {
        'state': 'finished',
        'finishCause': f'Give Up by {playerID}',
        'winner': winner
    }

    # TODO: Choose if delete or keep tile document for history
    # Delete tiles document
    tilesApi.delete({'gameID': gameID})
    # Update the info document
    updateInfoResult = infosApi.update({'id': gameID}, updateInfoDoc)

    app.logger.info(f"PUT 200 /play/giveup, {playerID} give up")
    return Response(response=json.dumps(updateInfoResult),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/<gameID>/<playerID>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getTiles(gameID, playerID):
    """Returns the player tiles and the board tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.readOne({'gameID': gameID})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(f"GET 404 /tile/{gameID}/{playerID}, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')


    racks = tilesDoc['racks']
    rack = next(filter(lambda rack: (rack['playerID'] == playerID), racks), None)

    if (rack == None):
        app.logger.error(f"GET 404 /tile/{gameID}/{playerID}, Player not in this game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in this game'}),
                        status=404,
                        mimetype='application/json')

    board = tilesDoc['board']

    app.logger.info(f"GET 200 /tile/{gameID}/{playerID}, Tiles success")
    return Response(response=json.dumps({'rack': rack, 'board': board}),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/board/<gameID>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getBoardTiles(gameID):
    """Returns only the board tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.readOne({'gameID': gameID})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(f"GET 404 /tiles/board/{gameID}, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    board = tilesDoc['board']

    app.logger.info(f"GET 200 /tiles/board/{gameID}, Tiles success")
    return Response(response=json.dumps(board),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/player/<gameID>/<playerID>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getPlayerTiles(gameID, playerID):
    """Returns only the player tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.readOne({'gameID': gameID})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(f"GET 404 /tile/player/{gameID}/{playerID}, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')


    racks = tilesDoc['racks']
    rack = next(filter(lambda rack: (rack['playerID'] == playerID), racks), None)

    if (rack is None):
        app.logger.error(f"GET 404 /tile/player/{gameID}/{playerID}, Player not in this game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in this game'}),
                        status=404,
                        mimetype='application/json')

    app.logger.info(f"GET 200 /tile/player/{gameID}/{playerID}, Tiles success")
    return Response(response=json.dumps(rack),
                    status=200,
                    mimetype='application/json')


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})


@app.route('/testsocket')
@cross_origin(supports_credentials=True)
def testSocket():
    return render_template('test.html', async_mode=socketio.async_mode)


@socketio.event
def my_event(message):
    app.logger.info('my_event:' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
        {
            'data': message['data'],
            'time': str(datetime.now()),
            'count': session['receive_count']
        })


@socketio.event
def my_broadcast_event(message):
    app.logger.info('my_broadcast_event:' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
        {'data': message['data'],
        'time': str(datetime.now()),
        'count': session['receive_count']},
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
    app.logger.info('on_close_room:' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    app.logger.info('my_room_event: ' + json.dumps(message))
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


@socketio.event
def what_are_my_rooms():
    app.logger.info('what_are_my_rooms:' + ', '.join(rooms()))
    emit('my_rooms', {'data': 'In rooms: ' + ', '.join(rooms())})


@socketio.event
def disconnect_request():
    app.logger.info('disconnect_request')

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
def playerJoinEvent(message):
    app.logger.info('playerJoin: ' + json.dumps(message))
    emit(
      'infoUpdate',
      {'event': 'playerJoin', 'playerID': message['playerID']},
      to=message['game']
    )


@socketio.event
def playerLeaveEvent(message):
    app.logger.info('playerLeave: ' + json.dumps(message))
    emit(
      'infoUpdate',
      {'event': 'playerLeave', 'playerID': message['playerID']},
      to=message['game']
    )


@socketio.event
def moveSubmit(message):
    app.logger.info('moveSubmit: ' + json.dumps(message))
    emit(
      'gameUpdate',
      {'event': 'moveSubmit', 'playerID': message['playerID']},
      to=message['game']
    )


@socketio.event
def connect():
    app.logger.info('connect')
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
