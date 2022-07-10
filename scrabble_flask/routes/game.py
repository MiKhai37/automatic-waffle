from uuid import uuid4
from datetime import datetime, timezone

from flask import Blueprint, Response, abort, json, request
from scrabble_flask.db import get_mongo_db

from scrabble_python import Scrabble

from scrabble_flask.db_helpers import (delete_doc_or_404, get_body_or_400,
                                  get_doc_or_404, get_n_docs)

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    GET: Get all (or n: query parameter) game documents
    POST: Create a new game document
    """
    if request.method == 'POST':
        req_params = ['name', 'nb_players', 'creator_id']
        opt_params = ['board_size', 'rack_size', 'lang', 'private']
        body = get_body_or_400(request, req_params, opt_params)
        creator_doc = get_doc_or_404('players', body['creator_id'])

        config = {
            'board_size': body.get('board_size', Scrabble.df_board_size),
            'rack_size': body.get('rack_size', Scrabble.df_rack_size),
            'lang': body.get('lang', Scrabble.df_lang)
        }

        new_game_doc = {
            'created_at': datetime.now(timezone.utc),
            'state': 'unstarted',
            'id': str(uuid4()),
            'creator_id': body['creator_id'],
            'name': body['name'],
            'nb_players': body['nb_players'],
            'players': [creator_doc],
            'config': config
        }

        insert_result = get_mongo_db('games').insert_doc(new_game_doc)
        return Response(response=json.dumps(insert_result),
                        status=201,
                        mimetype='application/json')

    n = request.args.get('n', 0, int)
    game_docs = get_n_docs('games', n)
    return Response(response=json.dumps(game_docs),
                    status=200,
                    mimetype='application/json')


@bp.route('/<game_id>', methods=['GET'])
def get_game(game_id):
    game_doc = get_doc_or_404('games', game_id)
    return Response(response=json.dumps(game_doc),
                    status=200,
                    mimetype='application/json')


@bp.route('/join', methods=['PUT'])
def join_game():
    req_params = ['game_id', 'player_id']
    body = get_body_or_400(request, req_params)
    player_doc = get_doc_or_404('players', body['player_id'])
    game_doc = get_doc_or_404('games', body['game_id'])
    players = game_doc['players']
    # Avoid duplicate join
    if body['player_id'] not in [player['id'] for player in players]:
        players.append(player_doc)
    update_result = get_mongo_db('games').update_one_doc(
        {'id': body['game_id']}, game_doc)
    return Response(response=json.dumps(update_result),
                    status=201,
                    mimetype='application/json')


@bp.route('/leave', methods=['PUT'])
def leave_game():
    req_params = ['game_id', 'player_id']
    body = get_body_or_400(request, req_params)
    player_doc = get_doc_or_404('players', body['player_id'])
    game_doc = get_doc_or_404('games', body['game_id'])
    players = game_doc['players']
    # Avoid duplicate remove
    if body['player_id'] in [player['id'] for player in players]:
        players.remove(player_doc)
    update_result = get_mongo_db('games').update_one_doc(
        {'id': body['game_id']}, game_doc)
    return Response(response=json.dumps(update_result),
                    status=201,
                    mimetype='application/json')


@bp.route('/start', methods=['PUT'])
def start_game():
    req_params = ['game_id']
    body = get_body_or_400(request, req_params)
    game_doc = get_doc_or_404('games', body['game_id'])
    abort(404)
