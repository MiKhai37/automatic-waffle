from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, abort, json, request
from scrabble_flask.db import get_mongo_db
from scrabble_flask.db_helpers import (get_body_or_400,
                                  get_doc_or_404)
from scrabble_python import Scrabble

bp = Blueprint('play', __name__, url_prefix='/play')


@bp.route('/', methods=['PUT'])
def index():
    req_params = ['game_id', 'player_id', 'tiles']
    body = get_body_or_400(request, req_params)
    game_doc = get_doc_or_404('games', body['game_id'])
    abort(404)


@bp.route('/abort', methods=['PUT'])
def abort_play():
    req_params = ['game_id', 'player_id']
    body = get_body_or_400(request, req_params)
    game_doc = get_doc_or_404('games', body['game_id'])
    abort(404)
