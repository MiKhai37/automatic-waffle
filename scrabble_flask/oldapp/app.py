import random
from threading import Lock
import logging
import uuid
from datetime import datetime
from flask import Flask, make_response, render_template, session, request, \
    copy_current_request_context, json, Response, abort, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_cors import CORS, cross_origin
from scrabble_flask.MongoAPI import MongoAPI
from ScrabbleLogic import Scrabble
from scrabble_flask.db_helpers import delete_doc_or_404, get_body_or_400, get_n_docs, get_doc_or_404

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_very_secret!'
CORS(app, support_credentials=True)
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(logging.DEBUG)

# TODO: User managment
# TODO: API security, Authentication


# Error Handlers
@app.errorhandler(404)
def resource_not_found(e):
    app.logger.error(f"404: {request.method} {request.endpoint}")
    return jsonify(error=str(e)), 404


@app.errorhandler(400)
def resource_not_found(e):
    app.logger.error(f"400: {request.method} {request.endpoint}")
    return jsonify(error=str(e)), 400


# Loggers
@app.before_request
def log_request():
    app.logger.debug(
        f"Request Info: endpoint: {request.method} {request.endpoint}")


@app.after_request
def log_response(res: Response):
    app.logger.debug(f'Response {res.response}')
    return res


# Routes
@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def index():
    return render_template('index.html')


@app.route('/ping', methods=['GET'])
@cross_origin(supports_credentials=True)
def ping_mongoDB():
    """
    Ping the current MongoDB Client,
    return the output plus its duration in milliseconds
    """
    return Response(response=json.dumps(MongoAPI().ping()))


@app.route('/player/random', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_random_player():
    n = request.args.get('n', 1, int)
    player_random_docs = MongoAPI('players').read_random_docs(n=n)
    return Response(response=json.dumps(player_random_docs),
                    status=200,
                    mimetype='application/json')


@app.route('/player/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_players():
    """Get all players documents matching query parameters"""
    data = request.json
    filt = data.get('Filter', {})

    player_docs = MongoAPI('players').read_many_docs(filt)

    return Response(response=json.dumps(player_docs),
                    status=200,
                    mimetype='application/json')


@app.route('/player', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_or_post_player():
    """
    GET: Get all (or n: query parameter) player documents
    POST: Create a new player document
    """
    if request.method == 'POST':
        body = get_body_or_400(request, ['pseudo'])

        new_player_doc = body
        new_player_doc.update({
            'created_at': datetime.utcnow(),
            'id': str(uuid.uuid4())
        })

        inserted_player_doc = MongoAPI('players').insert_doc(new_player_doc)

        return Response(response=json.dumps(inserted_player_doc),
                        status=201,
                        mimetype='application/json')

    n = request.args.get('n', 0, int)
    player_docs = get_n_docs('players', n)
    return Response(response=json.dumps(player_docs),
                    status=200,
                    mimetype='application/json')


@app.route('/player/<player_id>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def get_or_delete_player(player_id):
    """
    /player/<player_id> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding player document
    - DELETE endpoint

        Delete the corresponding player document
    """
    method = request.method
    if method == 'GET':
        doc_or_delete_result = get_doc_or_404('players', player_id)
    if method == 'DELETE':
        doc_or_delete_result = delete_doc_or_404('players', player_id)
    return Response(response=json.dumps(doc_or_delete_result),
                    status=201,
                    mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/join', methods=['PUT'])
@cross_origin(supports_credentials=True)
def player_join():
    """Add a player to the game, by adding it to its gameInfo document"""

    body = get_body_or_400(request, ['player_id', 'game_id'])

    player_id = body['player_id']
    game_id = body['game_id']

    player_doc = get_doc_or_404('players', player_id)
    info_doc = get_doc_or_404('infos', game_id)

    nb_players = info_doc['nb_players']
    players = info_doc['players']
    player_ids = map(lambda player: player['id'], players)

    if (player_id in player_ids):
        app.logger.error("PUT 403 /player/join, Player already in game")
        abort(403, 'Player already in game')

    if (len(players) >= nb_players):
        app.logger.error("PUT 403 /player/join, No place available")
        abort(403, 'No place')

    player_doc.pop('created_at', None)
    players.append(player_doc)

    update_result = MongoAPI('infos').update_one_doc(
        filt={'id': game_id}, data_to_put={'players': players})
    return Response(response=json.dumps(update_result),
                    status=200,
                    mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/leave', methods=['PUT'])
@cross_origin(supports_credentials=True)
def player_leave():
    """Remove a player from the game, by removing it from its gameInfo document"""

    body = get_body_or_400(request, ['player_id', 'game_id'])
    player_id = body['player_id']
    game_id = body['game_id']

    info_doc = get_doc_or_404('infos', player_id)

    players = info_doc['players']
    player_ids = map(lambda player: player['id'], players)

    if (player_id not in player_ids):
        app.logger.error("PUT 404 /player/leave, Player not in game")
        abort(404, 'Player not in game')

    player = list(filter(lambda player: (
        player['id'] == player_id), players))[0]
    # player = next(filter(lambda player: (player['id'] == player_id), players), None)
    # player = [player for player in players if player['id'] == player_id][0] # Or .pop() instead of [0]
    players.remove(player)
    update_result = MongoAPI('infos').update_one_doc(
        filt={'id': game_id}, data_to_put={'players': players})
    return Response(response=json.dumps(update_result),
                    status=200,
                    mimetype='application/json')


### Games Routes and Endpoints ###
@app.route('/game/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def search_games():
    """Get all infos documents matching query parameters"""
    data = request.json
    filt = data.get('Filter', {})

    infoDocs = MongoAPI('infos').read_many_docs(filt)

    return Response(response=json.dumps(infoDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/game', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_or_post_game():
    """
    GET: Get all (or n: query parameter) info documents
    POST: Create a new info document
    """
    if request.method == 'POST':
        required_parameters = ['creator_id', 'name', 'nb_players']
        body = get_body_or_400(request, required_parameters)

        creator_id = body.get('creator_id')
        name = body.get('name')
        nb_players = body.get('nb_players')

        creator_doc = get_doc_or_404('players', creator_id)
        creator_doc.pop('created_at', None)

        new_info_doc = {
            'creator_id': creator_id,
            'name': name,
            'nb_players': nb_players,
            'created_at': datetime.utcnow(),
            'id': str(uuid.uuid4()),
            'players': [creator_doc],
            'state': 'unstarted',
            'tiles_per_rack': body.get('tiles_per_rack', 7),
            'grid_size': body.get('grid_size', 7)
        }

        inserted_info_doc = MongoAPI('infos').insert_doc(new_info_doc)

        return Response(response=json.dumps(inserted_info_doc),
                        status=201,
                        mimetype='application/json')

    n = request.args.get('n', 0, int)
    game_docs = get_n_docs('infos', n)
    return Response(response=json.dumps(game_docs),
                    status=200,
                    mimetype='application/json')



@app.route('/game/<game_id>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def get_or_delete_game(game_id):
    """
    # game_idRoute
    ## /game/<game_id> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding gameInfo document
    - DELETE endpoint

        Delete the corresponding gameInfo document
    """
    method = request.method
    if method == 'GET':
        doc_or_delete_result = get_doc_or_404('infos', game_id)
    if method == 'DELETE':
        doc_or_delete_result = delete_doc_or_404('infos', game_id)
    return Response(response=json.dumps(doc_or_delete_result),
                    status=201,
                    mimetype='application/json')


@app.route('/play/start', methods=['POST'])
@cross_origin(supports_credentials=True)
def start_game():
    """Start the game, by updating its infoGame document, and creating a gameTiles documents"""
    body = get_body_or_400(request, ['game_id', 'player_id'])

    game_id = body['game_id']
    player_id = body['player_id']

    info_doc = get_doc_or_404('infos', game_id)

    # 403
    if (info_doc['creator_id'] != player_id):
        app.logger.error(
            "POST 403 /play/start, Only creator can start the game")
        abort(403, 'Only creator can start the game')

    # Avoid duplicate start operations
    if (info_doc['state'] != 'unstarted'):
        app.logger.error(
            "POST 403 /play/start, Game is already running, or finished")
        abort(403, 'Game already running')

    # TODO: implement override available places in frontend
    overridePlace = body.get('overridePlace', False)
    # Avoid game start with no required players
    if len(info_doc['players']) < info_doc['nb_players'] and not overridePlace:
        app.logger.error(
            f"POST 403 /play/start, Player(s) is(are) missing, {info_doc['nb_players'] - len(info_doc['players'])} place(s) available")
        abort(403, 'Game not full')

    # Updating the values of infoDoc
    # Note: The for loop mutates the player item in the players array in infoDoc
    for player in info_doc['players']:
        player['score'] = 0

    info_doc.update({
        'startedAt': datetime.utcnow(),
        'turn': 0,
        'state': 'running',
        'turnOffset': random.randint(0, len(info_doc['players']))
    })

    player_ids = list(map(lambda player: player['id'], info_doc['players']))
    info_doc['turnPlayerId'] = player_ids[(
        info_doc['turn'] + info_doc['turnOffset']) % info_doc['nb_players']]

    # Put the updated infoDoc to update
    MongoAPI('infos').update_one_doc({'id': game_id}, info_doc)

    scrabble = Scrabble(
        players=info_doc['players'], grid_size=info_doc['grid_size'], tiles_per_rack=info_doc['tiles_per_rack'])

    new_tile_doc = {
        'game_id': game_id,
        'board': scrabble.board,
        'racks': scrabble.racks,
        'purse': scrabble.purse
    }

    # Post the new tileDoc
    inserted_tile_doc = MongoAPI('tiles').insert_doc(new_tile_doc)

    return Response(response=json.dumps(inserted_tile_doc),
                    status=201,
                    mimetype='application/json')


@app.route('/play/giveup/', methods=['PUT'])
@cross_origin(supports_credentials=True)
def giveup_game():
    """Give up the game, by updating its infoGame document"""
    body = get_body_or_400(request, ['player_id', 'game_id'])
    player_id = body['player_id']
    game_id = body['game_id']

    info_doc = get_doc_or_404('infos', game_id)

    # Avoid give up of unstarted game
    if (info_doc['state'] == 'unstarted'):
        app.logger.error(
            "PUT 403 /play/giveup, Game is not started, giveup is imppossible")
        abort(403, 'Game unstarted')

    # Avoid duplicate give up
    if (info_doc['state'] == 'finished'):
        app.logger.error("PUT 403 /play/giveup, Game is already finished")
        abort(403, 'Game already finished')

    winner = "player with highest score"

    update_info_doc = {
        'stopped_at': datetime.utcnow(),
        'state': 'finished',
        'finishCause': f'Give Up by {player_id}',
        'winner': winner
    }

    # Update the info document
    update_info_result = MongoAPI('infos').update_one_doc(
        {'id': game_id}, update_info_doc)

    return Response(response=json.dumps(update_info_result),
                    status=200,
                    mimetype='application/json')


@app.route('/play/submit', methods=['PUT'])
@cross_origin(supports_credentials=True)
def play_submit():
    body = get_body_or_400(request, ['player_id', 'game_id', 'board', 'rack'])

    player_id = body['player_id']
    game_id = body['game_id']
    submit_board = body['board']
    submit_rack = body['rack']

    info_doc = get_doc_or_404('infos', game_id)

    if info_doc['state'] != 'running':
        app.logger.error("PUT 403 /play/submit, Game isn't running")
        abort(403, 'Game not running')

    tile_doc = get_doc_or_404('tiles', game_id, 'game_id')

    for tile in submit_board:
        tile['isSelected'] = False
        tile['isLocked'] = True

    for tile in submit_rack:
        tile['isSelected'] = False

    not_free_index = list(
        map(lambda tile: tile['location']['coords'], submit_rack))

    free_index = list(
        set(range(info_doc['tiles_per_rack'])) - set(not_free_index))

    purse = tile_doc['purse']
    for i in free_index:
        tile = purse.pop()
        tile['isSelected'] = False
        tile['isLocked'] = False
        tile['location'] = {'place': 'rack', 'coords': i}
        submit_rack.append(tile)

    submitRackBis = {'player_id': player_id, 'tiles': submit_rack}

    tile_doc['board'] = submit_board
    tile_doc['racks'] = list(map(lambda rack: rack if rack['player_id']
                                 != player_id else submitRackBis, tile_doc['racks']))
    tile_doc['purse'] = purse

    info_doc['turn'] = info_doc['turn'] + 1
    player_ids = list(map(lambda player: player['id'], info_doc['players']))
    info_doc['turnPlayerId'] = player_ids[(
        info_doc['turn'] + info_doc['turnOffset']) % info_doc['nb_players']]

    for player in info_doc['players']:
        if player['id'] == player_id:
            player['score'] = player['score'] + len(free_index)

    MongoAPI('infos').update_one_doc({'id': game_id}, info_doc)
    MongoAPI('tiles').update_one_doc({'game_id': game_id}, tile_doc)

    return Response(response=json.dumps({'status': 'OK'}),
                    status=200,
                    mimetype='application/json')


@app.route('/tile', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_all_tiles():
    """Returns all tiles documents"""
    n = request.args.get('n', 0, int)
    tile_docs = get_n_docs('tiles', n)
    return Response(response=json.dumps(tile_docs),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/<game_id>/<player_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_tiles(game_id, player_id):
    """Returns the player tiles and the board tiles"""
    tiles_doc = get_doc_or_404('tiles', game_id, 'game_id')

    racks = tiles_doc['racks']
    rack = next(filter(lambda rack: (
        rack['player_id'] == player_id), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/{game_id}/{player_id}, Player not in this game")
        abort(404, 'Player not found in the game')

    board = tiles_doc['board']

    return Response(response=json.dumps({'rack': rack, 'board': board}),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/board/<game_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_board_tiles(game_id):
    """Returns only the board tiles"""
    tiles_doc = get_doc_or_404('tiles', game_id, 'game_id')

    board = tiles_doc['board']

    return Response(response=json.dumps(board),
                    status=200,
                    mimetype='application/json')

# Useful ?


@app.route('/tile/player/<game_id>/<player_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_player_tiles(game_id, player_id):
    """Returns only the player tiles"""
    tiles_doc = get_doc_or_404('tiles', game_id, 'game_id')

    racks = tiles_doc['racks']
    rack = next(filter(lambda rack: (
        rack['player_id'] == player_id), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/player/{game_id}/{player_id}, Player not in this game")
        abort(404, 'Player in the game')

    return Response(response=json.dumps(rack),
                    status=200,
                    mimetype='application/json')


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
def player_join_event(message):
    app.logger.debug(f'SOCKETIO playerJoin: {json.dumps(message)}')
    emit(
        'infoUpdate',
        {'event': 'playerJoin', 'player_id': message['player_id']},
        to=f"lobby-{message['game_id']}"
    )


@socketio.event
def player_leave_event(message):
    app.logger.debug(f'SOCKETIO playerLeave: {json.dumps(message)}')
    emit(
        'infoUpdate',
        {'event': 'playerLeave', 'player_id': message['player_id']},
        to=f"lobby-{message['game_id']}"
    )


@socketio.event
def game_start_event(message):
    app.logger.debug(f'SOCKETIO gameStart:{json.dumps(message)}')
    emit('infoUpdate', {'event': 'gameStart'},
         to=f"lobby-{message['game_id']}")


@socketio.event
def move_submit_event(message):
    app.logger.debug(f'SOCKETIO moveSubmit: {json.dumps(message)}')
    emit(
        'gameUpdate',
        {'event': 'moveSubmit', 'player_id': message['player_id']},
        to=message['room']
    )


@socketio.on('connect')
def test_connection():
    app.logger.debug(f'SOCKETIO Client connected: {request.sid}')


@socketio.on('disconnect')
def test_disconnect():
    app.logger.debug(f'SOCKETIO Client disconnected: {request.sid}')


if __name__ == '__main__':
    socketio.run(app)
