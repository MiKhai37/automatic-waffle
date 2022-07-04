from flask import Flask, make_response, render_template, session, request, \
    copy_current_request_context, json, Response, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_cors import CORS, cross_origin
from MongoAPI import MongoAPI
import uuid
from threading import Lock
import logging
from datetime import datetime
import random
from ScrabbleLogic import Scrabble
from request_helpers import get_body_or_400, get_n_docs, get_or_delete_doc, get_doc_or_404

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_very_secret!'
CORS(app, support_credentials=True)
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
thread = None
thread_lock = Lock()

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(logging.DEBUG)

# TODO: manage login, and logged user
# games played, games won, game lost,
# highiest score, messages, challenge other user...)


@app.before_request
def log_request():
    app.logger.debug(
        f"Request Info: endpoint: {request.method} {request.endpoint}")


@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def index():
    """Get backend server status"""
    app.logger.debug('GET 200 /index')
    return render_template('index.html')


@app.route('/ping', methods=['GET'])
@cross_origin(supports_credentials=True)
def ping_mongoDB():
    """
    Ping the current MongoDB Client,
    return the output plus its duration in milliseconds
    """
    pingApi = MongoAPI()
    pingResponse = pingApi.ping()
    app.logger.debug(f"GET 200 /ping, {json.dumps(pingResponse)}")
    return Response(response=json.dumps(pingResponse))


@app.route('/player/random', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_random_player():
    n = request.args.get('n', 1, int)
    players_api = MongoAPI('players')
    player_random_docs = players_api.read_random_docs(n=n)
    return Response(response=json.dumps(player_random_docs),
                    status=200,
                    mimetype='application/json')


@app.route('/player', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_players():
    """Get all players documents, optional query parameter n (int): to limit the number of returned documents"""
    n = request.args.get('n', 0, int)
    resp = get_n_docs('players', n)
    app.logger.debug("GET 200 /player")
    return resp


@app.route('/player/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_players():
    """Get all players documents matching query parameters"""
    data = request.json
    filt = data.get('Filter', {})

    playersApi = MongoAPI('players')
    playerDocs = playersApi.read_many_docs(filt)

    app.logger.debug(f"GET 200 /player, count: {len(playerDocs)}")
    return Response(response=json.dumps(playerDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/player', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_player():
    """Create a new player, by inserting a new document in players collection"""
    body = get_body_or_400(request, ['pseudo'])

    newPlayerDoc = body
    newPlayerDoc['createdAt'] = datetime.utcnow()
    newPlayerDoc['id'] = str(uuid.uuid4())

    playersApi = MongoAPI('players')
    playerDoc = playersApi.insert_doc(newPlayerDoc)

    app.logger.debug(
        f"POST 201 /player,New Document Successfully Inserted, ID: {playerDoc['id']}")
    return Response(response=json.dumps(playerDoc),
                    status=201,
                    mimetype='application/json')


@app.route('/player/<playerId>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def get_or_delete_player(playerId):
    """
    /player/<playerId> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding player document
    - DELETE endpoint

        Delete the corresponding player document
    """
    # TODO: separate and create two func get and delete, better readability
    method = request.method
    resp = get_or_delete_doc(method, 'players', playerId)
    app.logger.debug(
        f"{method} 200 /player/{playerId}")
    return resp

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/join', methods=['PUT'])
@cross_origin(supports_credentials=True)
def player_join():
    """Add a player to the game, by adding it to its gameInfo document"""

    body = get_body_or_400(request, ['playerId', 'gameId'])

    player_id = body['playerId']
    game_id = body['gameId']

    player_doc = get_doc_or_404('players', player_id)
    info_doc = get_doc_or_404('infos', game_id)

    nb_players = info_doc['nbPlayers']
    players = info_doc['players']
    player_ids = map(lambda player: player['id'], players)

    if (player_id in player_ids):
        app.logger.error("PUT 403 /player/join, Player already in game")
        abort(403, 'Player already in game')

    if (len(players) >= nb_players):
        app.logger.error("PUT 403 /player/join, No place available")
        abort(403, 'No place')

    player_doc.pop('createdAt', None)
    players.append(player_doc)

    updateResult = MongoAPI('infos').update_one_doc(
        filt={'id': game_id}, dataToBeUpdated={'players': players})
    app.logger.debug(
        f"PUT 200 /player/join, Player {player_id} joins the game {game_id}")
    return Response(response=json.dumps(updateResult),
                    status=200,
                    mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/leave', methods=['PUT'])
@cross_origin(supports_credentials=True)
def player_leave():
    """Remove a player from the game, by removing it from its gameInfo document"""

    body = get_body_or_400(request, ['playerId', 'gameId'])
    player_id = body['playerId']
    game_id = body['gameId']

    info_api = MongoAPI('infos')

    info_doc = get_doc_or_404('infos', player_id)

    players = info_doc['players']
    playerIds = map(lambda player: player['id'], players)

    if (player_id not in playerIds):
        app.logger.error("PUT 404 /player/leave, Player not in game")
        abort(404, 'Player not in game')

    player = list(filter(lambda player: (
        player['id'] == player_id), players))[0]
    # player = next(filter(lambda player: (player['id'] == playerId), players), None)
    # player = [player for player in players if player['id'] == playerId][0] # Or .pop() instead of [0]
    players.remove(player)
    updateInfoResult = info_api.update_one_doc(
        filt={'id': game_id}, dataToBeUpdated={'players': players})
    app.logger.debug(
        f"PUT 200 /player/leave, Player {player_id} leaves the game {game_id}")
    return Response(response=json.dumps(updateInfoResult),
                    status=200,
                    mimetype='application/json')


### Games Routes and Endpoints ###
@app.route('/game', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_games():
    """Get all infoGame documents, optional query parameter n (int): to limit the number of returned documents"""
    n = request.args.get('n', 0, int)
    resp = get_n_docs('infos', n)
    app.logger.debug("GET 200 /game")
    return resp


@app.route('/game/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_games():
    """Get all infos documents matching query parameters"""
    data = request.json
    filt = data.get('Filter', {})

    infoApi = MongoAPI('infos')
    infoDocs = infoApi.read_many_docs(filt)

    app.logger.debug(f"GET 200 /player, count: {len(infoDocs)}")
    return Response(response=json.dumps(infoDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/game', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_game():
    """Create a new game, by inserting a new document in gameInfos collection"""
    body = get_body_or_400(request, ['creatorID', 'name', 'nbPlayers'])

    creator_id = body.get('creatorID')
    name = body.get('name')
    nb_players = body.get('nbPlayers')

    creator_doc = get_doc_or_404('players', creator_id)
    creator_doc.pop('createdAt', None)

    newInfoDoc = {'creatorID': creator_id, 'name': name,
                  'nbPlayers': nb_players, 'createdAt': datetime.utcnow()}

    newInfoDoc['id'] = str(uuid.uuid4())
    newInfoDoc['players'] = [creator_doc]
    newInfoDoc['state'] = 'unstarted'

    newInfoDoc['tilesPerRack'] = body.get('tilesPerRack', 7)
    newInfoDoc['gridSize'] = body.get('gridSize', 7)

    gameInfo = MongoAPI('infos').insert_doc(newInfoDoc)

    app.logger.debug(
        f"POST 201 /game, New Document Successfully Inserted, ID: {newInfoDoc['id']}")
    return Response(response=json.dumps(gameInfo),
                    status=201,
                    mimetype='application/json')


@app.route('/game/<gameId>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def get_or_delete_game(gameId):
    """
    # gameIdRoute
    ## /game/<gameId> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding gameInfo document
    - DELETE endpoint

        Delete the corresponding gameInfo document
    """
    # TODO: separate and create two func get and delete, better readability
    method = request.method
    if method == 'GET':
        print('GET')
    if method == 'DELETE':
        print('DELETE')
    resp = get_or_delete_doc(method, 'infos', gameId)
    app.logger.debug(
        f"{method} 200 /game/{gameId}")
    return resp


@app.route('/play/start', methods=['POST'])
@cross_origin(supports_credentials=True)
def start_game():
    """Start the game, by updating its infoGame document, and creating a gameTiles documents"""
    body = get_body_or_400(request, ['gameId', 'playerId'])

    gameId = body['gameId']
    playerId = body['playerId']

    info_doc = get_doc_or_404('infos', gameId)
    info_doc['startedAt'] = datetime.utcnow()

    # 403
    if (info_doc['creatorID'] != playerId):
        app.logger.error(
            "POST 403 /play/start, Only creator can start the game")
        abort(403, 'Only creator can start the game')

    # Avoid duplicate start operations
    if (info_doc['state'] != 'unstarted'):
        app.logger.error(
            "POST 403 /play/start, Game is already running, or finished")
        abort(403, 'Game already running')

    # TODO: implement override available places in frontend
    # overridePlace = request.json['overridePlace']
    overridePlace = False
    # Avoid game start with no required players
    if len(info_doc['players']) < info_doc['nbPlayers'] and not overridePlace:
        app.logger.error(
            f"POST 403 /play/start, Player(s) is(are) missing, {info_doc['nbPlayers'] - len(info_doc['players'])} place(s) available")
        abort(403, 'Game not full')

    # Updating the values of infoDoc
    # Note: The for loop mutates the player item in the players array in infoDoc
    for player in info_doc['players']:
        player['score'] = 0

    info_doc['turn'] = 0
    info_doc['state'] = 'running'
    info_doc['turnOffset'] = random.randint(0, len(info_doc['players']))

    playerIds = list(map(lambda player: player['id'], info_doc['players']))
    info_doc['turnPlayerId'] = playerIds[(
        info_doc['turn'] + info_doc['turnOffset']) % info_doc['nbPlayers']]

    # Put the updated infoDoc to update
    MongoAPI('infos').update_one_doc({'id': gameId}, info_doc)

    scrabble = Scrabble(
        players=info_doc['players'], gridSize=info_doc['gridSize'], tilesPerRack=info_doc['tilesPerRack'])
    racks = scrabble.racks
    purse = scrabble.purse
    board = scrabble.board

    newTileDoc = {'gameId': gameId, 'board': board,
                  'racks': racks, 'purse': purse}

    # Post the new tileDoc
    gameTilesDoc = MongoAPI('tiles').insert_doc(newTileDoc)

    app.logger.debug("POST 201 /play/start, Game has been started")
    return Response(response=json.dumps(gameTilesDoc),
                    status=201,
                    mimetype='application/json')


@app.route('/play/giveup/', methods=['PUT'])
@cross_origin(supports_credentials=True)
def giveup_game():
    """Give up the game, by updating its infoGame document"""
    body = get_body_or_400(request, ['playerId', 'gameId'])
    playerId = body['playerId']
    gameId = body['gameId']

    info_doc = get_doc_or_404('infos', gameId)

    # Avoid give up of unstarted game
    if (info_doc['state'] == 'unstarted'):
        app.logger.error(
            "PUT 403 /play/giveup, Game is not started, giveup is imppossible")
        abort(403, 'Game unstarted')

    # Avoid duplicate give up
    if (info_doc['state'] == 'finished'):
        app.logger.error("PUT 403 /play/giveup, Game is already finished")
        abort(403, 'Game already finished')
    # TODO: select the highest score
    winner = "player with highest score"

    updateInfoDoc = {
        'stoppedAt': datetime.utcnow(),
        'state': 'finished',
        'finishCause': f'Give Up by {playerId}',
        'winner': winner
    }

    # TODO: Choose if delete or keep tile document for history
    # Delete tiles document
    MongoAPI('tiles').delete_doc({'gameId': gameId})
    # Update the info document
    updateInfoResult = MongoAPI('infos').update_one_doc(
        {'id': gameId}, updateInfoDoc)

    app.logger.debug(f"PUT 200 /play/giveup, {playerId} give up")
    return Response(response=json.dumps(updateInfoResult),
                    status=200,
                    mimetype='application/json')

# TODO: Implement move validity, points counting


@app.route('/play/submit', methods=['PUT'])
@cross_origin(supports_credentials=True)
def play_submit():
    body = get_body_or_400(request, ['playerId', 'gameId', 'board', 'rack'])

    playerId = body['playerId']
    gameId = body['gameId']
    submitBoard = body['board']
    submitRack = body['rack']

    info_doc = get_doc_or_404('infos', gameId)

    if info_doc['state'] != 'running':
        app.logger.error("PUT 403 /play/submit, Game isn't running")
        abort(403, 'Game not running')

    tiles_doc = get_doc_or_404('tiles', gameId, 'gameId')

    for tile in submitBoard:
        tile['isSelected'] = False
        tile['isLocked'] = True

    for tile in submitRack:
        tile['isSelected'] = False

    indexToNotFill = list(
        map(lambda tile: tile['location']['coords'], submitRack))

    indexToFill = list(
        set(range(info_doc['tilesPerRack'])) - set(indexToNotFill))

    purse = tiles_doc['purse']
    for i in indexToFill:
        tile = purse.pop()
        tile['isSelected'] = False
        tile['isLocked'] = False
        tile['location'] = {'place': 'rack', 'coords': i}
        submitRack.append(tile)

    submitRackBis = {'playerId': playerId, 'tiles': submitRack}

    tiles_doc['board'] = submitBoard
    tiles_doc['racks'] = list(map(lambda rack: rack if rack['playerId']
                                  != playerId else submitRackBis, tiles_doc['racks']))
    tiles_doc['purse'] = purse

    info_doc['turn'] = info_doc['turn'] + 1
    playerIds = list(map(lambda player: player['id'], info_doc['players']))
    info_doc['turnPlayerId'] = playerIds[(
        info_doc['turn'] + info_doc['turnOffset']) % info_doc['nbPlayers']]

    for player in info_doc['players']:
        if player['id'] == playerId:
            player['score'] = player['score'] + len(indexToFill)

    MongoAPI('infos').update_one_doc({'id': gameId}, info_doc)
    MongoAPI('tiles').update_one_doc({'gameId': gameId}, tiles_doc)

    app.logger.debug("PUT 200 /play/submit")
    return Response(response=json.dumps({'status': 'OK'}),
                    status=200,
                    mimetype='application/json')


# TODO: secure this route
@app.route('/tile', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_all_tiles():
    """Returns all tiles documents"""
    n = request.args.get('n', 0, int)
    app.logger.debug("GET 200 /tile")
    return get_n_docs('tiles', n)


@app.route('/tile/<gameId>/<playerId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_tiles(gameId, playerId):
    """Returns the player tiles and the board tiles"""
    tiles_doc = get_doc_or_404('tiles', gameId, 'gameId')

    racks = tiles_doc['racks']
    rack = next(filter(lambda rack: (
        rack['playerId'] == playerId), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/{gameId}/{playerId}, Player not in this game")
        abort(404, 'Player not found in the game')

    board = tiles_doc['board']

    app.logger.debug(f"GET 200 /tile/{gameId}/{playerId}, Tiles success")
    return Response(response=json.dumps({'rack': rack, 'board': board}),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/board/<gameId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_board_tiles(gameId):
    """Returns only the board tiles"""
    tiles_doc = get_doc_or_404('tiles', gameId, 'gameId')

    board = tiles_doc['board']

    app.logger.debug(f"GET 200 /tiles/board/{gameId}, Tiles success")
    return Response(response=json.dumps(board),
                    status=200,
                    mimetype='application/json')

# Useful ?


@app.route('/tile/player/<gameId>/<playerId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_player_tiles(gameId, playerId):
    """Returns only the player tiles"""
    tiles_doc = get_doc_or_404('tiles', gameId, 'gameId')

    racks = tiles_doc['racks']
    rack = next(filter(lambda rack: (
        rack['playerId'] == playerId), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/player/{gameId}/{playerId}, Player not in this game")
        abort(404, 'Player in the game')

    app.logger.debug(
        f"GET 200 /tile/player/{gameId}/{playerId}, Tiles success")
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
    app.logger.debug(f'SOCKETIO my_event:{json.dumps(message)}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {
             'data': message['data'],
             'time': str(datetime.now()),
             'count': session['receive_count']
         })


@socketio.event
def my_broadcast_event(message):
    app.logger.debug(f'SOCKETIO my_broadcast_event:{json.dumps(message)}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'],
          'time': str(datetime.now()),
          'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    app.logger.debug(f'SOCKETIO join:{json.dumps(message)}')
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    app.logger.debug(f'SOCKETIO leave:{json.dumps(message)}')
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    app.logger.debug(f'SOCKETIO on_close_room:{json.dumps(message)}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    app.logger.debug(f'SOCKETIO my_room_event: {json.dumps(message)}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


@socketio.event
def what_are_my_rooms():
    app.logger.debug('SOCKETIO what_are_my_rooms:' + ', '.join(rooms()))
    emit('my_rooms', {'data': 'In rooms: ' + ', '.join(rooms())})


@socketio.event
def disconnect_request():
    app.logger.debug('SOCKETIO disconnect_request')

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
    app.logger.debug(f'SOCKETIO playerJoin: {json.dumps(message)}')
    emit(
        'infoUpdate',
        {'event': 'playerJoin', 'playerId': message['playerId']},
        to=f"lobby-{message['gameId']}"
    )


@socketio.event
def playerLeaveEvent(message):
    app.logger.debug(f'SOCKETIO playerLeave: {json.dumps(message)}')
    emit(
        'infoUpdate',
        {'event': 'playerLeave', 'playerId': message['playerId']},
        to=f"lobby-{message['gameId']}"
    )


@socketio.event
def gameStartEvent(message):
    app.logger.debug(f'SOCKETIO gameStart:{json.dumps(message)}')
    emit('infoUpdate', {'event': 'gameStart'}, to=f"lobby-{message['gameId']}")


@socketio.event
def moveSubmitEvent(message):
    app.logger.debug(f'SOCKETIO moveSubmit: {json.dumps(message)}')
    emit(
        'gameUpdate',
        {'event': 'moveSubmit', 'playerId': message['playerId']},
        to=message['room']
    )


@socketio.event
def connect():
    app.logger.debug('SOCKETIO connect')
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('connect')
def test_connection():
    app.logger.debug(f'SOCKETIO Client connected: {request.sid}')


@socketio.on('disconnect')
def test_disconnect():
    app.logger.debug(f'SOCKETIO Client disconnected: {request.sid}')


if __name__ == '__main__':
    socketio.run(app)
