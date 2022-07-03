from flask import Flask, make_response, render_template, session, request, \
    copy_current_request_context, json, Response
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
def requestLog():
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
def pingMongoDB():
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

    playersApi = MongoAPI('players')
    playerDocs = playersApi.read_many_docs(n=n)

    app.logger.debug(f"GET 200 /player, count: {len(playerDocs)}")
    return Response(response=json.dumps(playerDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/player/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def searchPlayers():
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
    required = ['pseudo']
    body = request.json

    if any(prop not in body for prop in required):
        app.logger.error(f"POST 404 /player, Missing properties, {required}")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Required property(ies) in body request is(are) missing', 'reqProps': required}),
                        status=400,
                        mimetype='application/json')

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
    playersApi = MongoAPI('players')

    if request.method == 'GET':
        playerDoc = playersApi.read_one_doc({'id': playerId})

        if (playerDoc.get('Code') == 404):
            app.logger.error(
                f"GET 404 /player/{playerId}, This player doesn't exist")
            return Response(response=json.dumps({'err': True, 'errMsg': "This player doesn't exist"}),
                            status=404,
                            mimetype='application/json')

        app.logger.debug(
            f"GET 200 /player/{playerId}, pseudo: {playerDoc['pseudo']}")
        return Response(response=json.dumps(playerDoc),
                        status=200,
                        mimetype='application/json')

    if request.method == 'DELETE':
        if ('Test' in playerId):
            app.logger.error(
                f"DELETE 403 /player/{playerId}, It's a test document, its deletion is unallowed")
            return Response(response=json.dumps({'err': True, 'errMsg': "It's a test document, its deletion is unallowed"}),
                            status=403,
                            mimetype='application/json')

        deletePlayerResult = playersApi.delete_doc({'id': playerId})

        app.logger.debug(
            f"DELETE {deletePlayerResult['Code']} /player/{playerId}, Player {deletePlayerResult['Status']}")
        return Response(response=json.dumps(deletePlayerResult),
                        status=deletePlayerResult['Code'],
                        mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/join', methods=['PUT'])
@cross_origin(supports_credentials=True)
def playerJoin():
    """Add a player to the game, by adding it to its gameInfo document"""
    playerId = request.json['playerId']
    gameId = request.json['gameId']

    playersApi = MongoAPI('players')
    infosApi = MongoAPI('infos')

    playerDoc = playersApi.read_one_doc({'id': playerId})
    infoDoc = infosApi.read_one_doc({'id': gameId})

    if (playerDoc.get('Code') == 404 or infoDoc.get('Code') == 404):
        app.logger.error("PUT 404 /player/join, Player or Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': "Player or Game not found"}),
                        status=404,
                        mimetype='application/json')

    nbPlayers = infoDoc['nbPlayers']
    players = infoDoc['players']
    playerIds = map(lambda player: player['id'], players)

    if (playerId in playerIds):
        app.logger.error("PUT 403 /player/join, Player already in game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player already in game'}),
                        status=403,
                        mimetype='application/json')

    if (len(players) >= nbPlayers):
        app.logger.error("PUT 403 /player/join, No place available")
        return Response(response=json.dumps({'err': True, 'errMsg': 'No place available'}),
                        status=403,
                        mimetype='application/json')

    playerDoc.pop('createdAt', None)
    players.append(playerDoc)

    updateResult = infosApi.update_one_doc(
        filt={'id': gameId}, dataToBeUpdated={'players': players})
    app.logger.debug(
        f"PUT 200 /player/join, Player {playerId} joins the game {gameId}")
    return Response(response=json.dumps(updateResult),
                    status=200,
                    mimetype='application/json')

# TODO: Search update operator to make the operation without finding the document first


@app.route('/player/leave', methods=['PUT'])
@cross_origin(supports_credentials=True)
def playerLeave():
    """Remove a player from the game, by removing it from its gameInfo document"""
    playerId = request.json['playerId']
    gameId = request.json['gameId']

    infosApi = MongoAPI('infos')
    infoDoc = infosApi.read_one_doc({'id': gameId})

    if (infoDoc.get('Code') == 404):
        app.logger.error("PUT 404 /player/leave, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    players = infoDoc['players']
    playerIds = map(lambda player: player['id'], players)

    if (playerId not in playerIds):
        app.logger.error("PUT 404 /player/leave, Player not in game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in game'}),
                        status=404,
                        mimetype='application/json')

    player = list(filter(lambda player: (
        player['id'] == playerId), players))[0]
    # player = next(filter(lambda player: (player['id'] == playerId), players), None)
    # player = [player for player in players if player['id'] == playerId][0] # Or .pop() instead of [0]
    players.remove(player)
    updateInfoResult = infosApi.update_one_doc(
        filt={'id': gameId}, dataToBeUpdated={'players': players})
    app.logger.debug(
        f"PUT 200 /player/leave, Player {playerId} leaves the game {gameId}")
    return Response(response=json.dumps(updateInfoResult),
                    status=200,
                    mimetype='application/json')


### Games Routes and Endpoints ###
@app.route('/game', methods=['GET'])
@cross_origin(supports_credentials=True)
def getGames():
    """Get all infoGame documents, optional query parameter n (int): to limit the number of returned documents"""
    n = request.args.get('n', 0, int)
    infosApi = MongoAPI('infos')
    infoDocs = infosApi.read_many_docs(n=n)

    app.logger.debug(f'GET 200 /games, count: {len(infoDocs)}')
    return Response(response=json.dumps(infoDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/game/search', methods=['GET'])
@cross_origin(supports_credentials=True)
def searchGames():
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
def postGame():
    """Create a new game, by inserting a new document in gameInfos collection"""
    data = request.json

    required = ['creatorID', 'name', 'nbPlayers']

    if any(prop not in data for prop in required):
        app.logger.error(f"POST 404 /game, Missing properties, {required}")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Required property(ies) in body request is(are) missing', 'required': required}),
                        status=400,
                        mimetype='application/json')

    creatorID = data.get('creatorID')
    name = data.get('name')
    nbPlayers = data.get('nbPlayers')

    playersApi = MongoAPI('players')
    creatorPlayerDoc = playersApi.read_one_doc({'id': creatorID})

    if creatorPlayerDoc.get('Code') == 404:
        app.logger.error("POST 404 /game, Creator not found")
        return Response(response=json.dumps({'err': True, 'errMsg': "Creator not found"}),
                        status=404,
                        mimetype='application/json')

    creatorPlayerDoc.pop('createdAt', None)

    newInfoDoc = {'creatorID': creatorID, 'name': name, 'nbPlayers': nbPlayers, 'createdAt': datetime.utcnow()}


    newInfoDoc['id'] = str(uuid.uuid4())
    newInfoDoc['players'] = [creatorPlayerDoc]
    newInfoDoc['state'] = 'unstarted'

    newInfoDoc['tilesPerRack'] = data.get('tilesPerRack', 7)
    newInfoDoc['gridSize'] = data.get('gridSize', 7)

    infosApi = MongoAPI('infos')
    gameInfo = infosApi.insert_doc(newInfoDoc)

    app.logger.debug(
        f"POST 201 /game, New Document Successfully Inserted, ID: {newInfoDoc['id']}")
    return Response(response=json.dumps(gameInfo),
                    status=201,
                    mimetype='application/json')


@app.route('/game/<gameId>', methods=['GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def getOrDeleteGame(gameId):
    """
    # gameIdRoute
    ## /game/<gameId> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding gameInfo document
    - DELETE endpoint

        Delete the corresponding gameInfo document
    """
    infosApi = MongoAPI('infos')

    if request.method == 'GET':
        infoDoc = infosApi.read_one_doc({'id': gameId})

        if (infoDoc.get('Code') == 404):
            app.logger.error(f"GET 404 /game/{gameId}, Game not found")
            return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                            status=404,
                            mimetype='application/json')

        app.logger.debug(f"GET 200 /game/{gameId}, name: {infoDoc['name']}")
        return Response(response=json.dumps(infoDoc),
                        status=200,
                        mimetype='application/json')

    # TODO: Also remove the gameTile document if game was started
    if request.method == 'DELETE':
        if ('Test' in gameId):
            app.logger.error(
                f"DELETE 403 /game/{gameId}, It's a test document, its deletion is unallowed")
            return Response(response=json.dumps({'err': True, 'errMsg': "It's a test document, its deletion is unallowed"}),
                            status=403,
                            mimetype='application/json')

        infosApi = MongoAPI('infos')
        deleteGameResult = infosApi.delete_doc({'id': gameId})

        app.logger.debug(
            f"DELETE {deleteGameResult['Code']} /game/{gameId}, Game {deleteGameResult['Status']}")
        return Response(response=json.dumps(deleteGameResult),
                        status=deleteGameResult['Code'],
                        mimetype='application/json')


# TODO: Game logic to move in another pyfile
frLettersDistribution = [['*', 2, 0], ['E', 16, 1], ['A', 9, 1], ['I', 8, 1], ['D', 6, 1], ['N', 8, 1], ['O', 6, 1], ['R', 6, 1], ['S', 6, 1], ['T', 6, 1], ['G', 4, 2], [
    'H', 3, 2], ['L', 3, 2], ['K', 3, 3], ['W', 3, 3], ['M', 2, 4], ['U', 2, 4], ['Y', 2, 4], ['P', 2, 5], ['V', 2, 5], ['B', 1, 8], ['F', 1, 8], ['J', 1, 10]]


def createInitialPurse(lettersDistribution):
    initialPurse = []
    for letter in lettersDistribution:
        initialPurse += [{'letter': letter[0], 'point': letter[2],
                          'id': str(uuid.uuid4())} for _ in range(letter[1])]

    return initialPurse


def drawInitialRacksAndPurse(initialPurse: list, players, tilesPerRack):
    # clean code, not parameter mutations
    purse = initialPurse.copy()
    # better to shuffle the purse once and pop tile from the end, than to pop tile from random index
    random.shuffle(purse)

    racks = []
    for player in players:
        tiles = []
        for i in range(tilesPerRack):
            tile = purse.pop()
            tile['isSelected'] = False
            tile['isLocked'] = False
            tile['location'] = {'place': 'rack', 'coords': i}
            tiles.append(tile)
        racks.append({'playerId': player['id'], 'tiles': tiles})

    return purse, racks


def drawTile(purse):
    # clean code, no parameter mutations
    purseCopy = purse.copy()
    tile = purseCopy.pop()
    return purseCopy, tile


@app.route('/play/start', methods=['POST'])
@cross_origin(supports_credentials=True)
def startGame():
    """Start the game, by updating its infoGame document, and creating a gameTiles documents"""
    gameId = request.json['gameId']
    playerId = request.json['playerId']

    infosApi = MongoAPI('infos')
    infoDoc = infosApi.read_one_doc({'id': gameId})
    infoDoc['startedAt'] = datetime.utcnow()

    # 404
    if (infoDoc.get('Code') == 404):
        app.logger.error("POST 404 /play/start, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    # 403
    if (infoDoc['creatorID'] != playerId):
        app.logger.error(
            "POST 403 /play/start, Only creator can start the game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Only creator can start the game'}),
                        status=403,
                        mimetype='application/json')

    # Avoid duplicate start operations
    if (infoDoc['state'] != 'unstarted'):
        app.logger.error(
            "POST 403 /play/start, Game is already running, or finished")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game is already running, or finished'}),
                        status=403,
                        mimetype='application/json')

    # TODO: implement override available places in frontend
    # overridePlace = request.json['overridePlace']
    overridePlace = False
    # Avoid game start with no required players
    if len(infoDoc['players']) < infoDoc['nbPlayers'] and not overridePlace:
        app.logger.error(
            f"POST 403 /play/start, Player(s) is(are) missing, {infoDoc['nbPlayers'] - len(infoDoc['players'])} place(s) available")
        return Response(response=json.dumps({'err': True, 'errMsg': f"Player(s) is(are) missing, {infoDoc['nbPlayers'] - len(infoDoc['players'])} place(s) available"}),
                        status=403,
                        mimetype='application/json')

    tilesApi = MongoAPI('tiles')

    # Updating the values of infoDoc
    # Note: The for loop mutates the player item in the players array in infoDoc
    for player in infoDoc['players']:
        player['score'] = 0

    infoDoc['turn'] = 0
    infoDoc['state'] = 'running'
    infoDoc['turnOffset'] = random.randint(0, len(infoDoc['players']))

    playerIds = list(map(lambda player: player['id'], infoDoc['players']))
    infoDoc['turnPlayerId'] = playerIds[(
        infoDoc['turn'] + infoDoc['turnOffset']) % infoDoc['nbPlayers']]

    # Put the updated infoDoc to update
    infosApi.update_one_doc({'id': gameId}, infoDoc)

    scrabble = Scrabble(
        players=infoDoc['players'], gridSize=infoDoc['gridSize'], tilesPerRack=infoDoc['tilesPerRack'])
    racks = scrabble.racks
    purse = scrabble.purse
    board = scrabble.board

    newTileDoc = {'gameId': gameId, 'board': board,
                  'racks': racks, 'purse': purse}

    # Post the new tileDoc
    gameTilesDoc = tilesApi.insert_doc(newTileDoc)

    app.logger.debug("POST 201 /play/start, Game has been started")
    return Response(response=json.dumps(gameTilesDoc),
                    status=201,
                    mimetype='application/json')


@app.route('/play/giveup/', methods=['PUT'])
@cross_origin(supports_credentials=True)
def giveupGame():
    """Give up the game, by updating its infoGame document"""
    playerId = request.json['playerId']
    gameId = request.json['gameId']

    infosApi = MongoAPI('infos')
    tilesApi = MongoAPI('tiles')

    infoDoc = infosApi.read_one_doc({'id': gameId})
    if (infoDoc.get('Code') == 404):
        app.logger.error("PUT 404 /play/giveup, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    # Avoid give up of unstarted game
    if (infoDoc['state'] == 'unstarted'):
        app.logger.error(
            "PUT 403 /play/giveup, Game is not started, giveup is imppossible")
        return Response(response=json.dumps({'err': True, 'errMsg': ' Game is not started, giveup is impossible'}),
                        status=403,
                        mimetype='application/json')

    # Avoid duplicate give up
    if (infoDoc['state'] == 'finished'):
        app.logger.error("PUT 403 /play/giveup, Game is already finished")
        return Response(response=json.dumps({'err': True, 'errMsg': ' Game is already finished'}),
                        status=403,
                        mimetype='application/json')
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
    tilesApi.delete_doc({'gameId': gameId})
    # Update the info document
    updateInfoResult = infosApi.update_one_doc({'id': gameId}, updateInfoDoc)

    app.logger.debug(f"PUT 200 /play/giveup, {playerId} give up")
    return Response(response=json.dumps(updateInfoResult),
                    status=200,
                    mimetype='application/json')

# TODO: Implement move validity, points counting


@app.route('/play/submit', methods=['PUT'])
@cross_origin(supports_credentials=True)
def playSubmit():
    data = request.json

    playerId = data['playerId']
    gameId = data['gameId']
    submitBoard = data['board']
    submitRack = data['rack']

    infosApi = MongoAPI('infos')
    tilesApi = MongoAPI('tiles')
    infosDoc = infosApi.read_one_doc({'id': gameId})

    if infosDoc.get('Code') == 404:
        app.logger.error("PUT 404 /play/submit, Game not found")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found'}),
                        status=404,
                        mimetype='application/json')

    if infosDoc['state'] != 'running':
        app.logger.error("PUT 403 /play/submit, Game isn't running")
        return Response(response=json.dumps({'err': True, 'errMsg': "Game isn't running"}),
                        status=404,
                        mimetype='application/json')

    tilesDoc = tilesApi.read_one_doc({'gameId': gameId})

    for tile in submitBoard:
        tile['isSelected'] = False
        tile['isLocked'] = True

    for tile in submitRack:
        tile['isSelected'] = False

    indexToNotFill = list(
        map(lambda tile: tile['location']['coords'], submitRack))

    indexToFill = list(
        set(range(infosDoc['tilesPerRack'])) - set(indexToNotFill))

    purse = tilesDoc['purse']
    for i in indexToFill:
        tile = purse.pop()
        tile['isSelected'] = False
        tile['isLocked'] = False
        tile['location'] = {'place': 'rack', 'coords': i}
        submitRack.append(tile)

    submitRackBis = {'playerId': playerId, 'tiles': submitRack}

    tilesDoc['board'] = submitBoard
    tilesDoc['racks'] = list(map(lambda rack: rack if rack['playerId']
                             != playerId else submitRackBis, tilesDoc['racks']))
    tilesDoc['purse'] = purse

    infosDoc['turn'] = infosDoc['turn'] + 1
    playerIds = list(map(lambda player: player['id'], infosDoc['players']))
    infosDoc['turnPlayerId'] = playerIds[(
        infosDoc['turn'] + infosDoc['turnOffset']) % infosDoc['nbPlayers']]

    for player in infosDoc['players']:
        if player['id'] == playerId:
            player['score'] = player['score'] + len(indexToFill)

    infosUpdateResult = infosApi.update_one_doc({'id': gameId}, infosDoc)
    tilesUpdateResult = tilesApi.update_one_doc({'gameId': gameId}, tilesDoc)

    app.logger.debug("PUT 200 /play/submit")
    return Response(response=json.dumps({'status': 'OK'}),
                    status=200,
                    mimetype='application/json')


# TODO: secure this route
@app.route('/tile', methods=['GET'])
@cross_origin(supports_credentials=True)
def getAllTiles():
    """Returns all tiles documents"""
    tilesApi = MongoAPI('tiles')
    tilesDocs = tilesApi.read_many_docs()

    app.logger.debug(f"GET 200 /tile, count: {len(tilesDocs)}")
    return Response(response=json.dumps(tilesDocs),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/<gameId>/<playerId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getTiles(gameId, playerId):
    """Returns the player tiles and the board tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.read_one_doc({'gameId': gameId})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(
            f"GET 404 /tile/{gameId}/{playerId}, Game not found or unstarted")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found or unstarted'}),
                        status=404,
                        mimetype='application/json')

    racks = tilesDoc['racks']
    rack = next(filter(lambda rack: (
        rack['playerId'] == playerId), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/{gameId}/{playerId}, Player not in this game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in this game'}),
                        status=404,
                        mimetype='application/json')

    board = tilesDoc['board']

    app.logger.debug(f"GET 200 /tile/{gameId}/{playerId}, Tiles success")
    return Response(response=json.dumps({'rack': rack, 'board': board}),
                    status=200,
                    mimetype='application/json')


@app.route('/tile/board/<gameId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getBoardTiles(gameId):
    """Returns only the board tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.read_one_doc({'gameId': gameId})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(
            f"GET 404 /tiles/board/{gameId}, Game not found ou unstarted")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found or unstarted'}),
                        status=404,
                        mimetype='application/json')

    board = tilesDoc['board']

    app.logger.debug(f"GET 200 /tiles/board/{gameId}, Tiles success")
    return Response(response=json.dumps(board),
                    status=200,
                    mimetype='application/json')

# Useful ?


@app.route('/tile/player/<gameId>/<playerId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getPlayerTiles(gameId, playerId):
    """Returns only the player tiles"""
    tilesApi = MongoAPI('tiles')
    tilesDoc = tilesApi.read_one_doc({'gameId': gameId})
    if (tilesDoc.get('Code') == 404):
        app.logger.error(
            f"GET 404 /tile/player/{gameId}/{playerId}, Game not found or unstarted")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Game not found or unstarted'}),
                        status=404,
                        mimetype='application/json')

    racks = tilesDoc['racks']
    rack = next(filter(lambda rack: (
        rack['playerId'] == playerId), racks), None)

    if (rack is None):
        app.logger.error(
            f"GET 404 /tile/player/{gameId}/{playerId}, Player not in this game")
        return Response(response=json.dumps({'err': True, 'errMsg': 'Player not in this game'}),
                        status=404,
                        mimetype='application/json')

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


def validate_body(request, required_params):
    body = request.json
    if any(param not in body for param in required_params):
        return Response(response=json.dumps({'errMsg': 'Required parameter in body request is missing'}),
                        status=400,
                        mimetype='application/json')
    return body



if __name__ == '__main__':
    socketio.run(app)
