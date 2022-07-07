import uuid
from datetime import datetime, timezone

from flask import Blueprint, Response, json, request


from .db import get_mongo_db
from .db_helpers import (delete_doc_or_404, get_body_or_400,
                              get_doc_or_404, get_n_docs)


bp = Blueprint('player', __name__, url_prefix='/player')


@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    GET: Get all (or n: query parameter) player documents
    POST: Create a new player document
    """
    if request.method == 'POST':
        body = get_body_or_400(request, ['pseudo'])

        new_player_doc = body
        new_player_doc.update({
            'created_at': datetime.now(timezone.utc),
            'id': str(uuid.uuid4())
        })

        insert_result = get_mongo_db('players').insert_doc(new_player_doc)

        return Response(response=json.dumps(insert_result),
                        status=201,
                        mimetype='application/json')

    n = request.args.get('n', 0, int)
    player_docs = get_n_docs('players', n)
    return Response(response=json.dumps(player_docs),
                    status=200,
                    mimetype='application/json')


@bp.route('/<player_id>', methods=['GET', 'DELETE'])
def get_or_delete_player(player_id):
    """
    /player/<player_id> route, 2 endpoints GET and DELETE

    - GET endpoint

        Returns the corresponding player document
    - DELETE endpoint

        Delete the corresponding player document
    """
    if request.method == 'DELETE':
        response_result = delete_doc_or_404('players', player_id)
        status = 201
    else:
        response_result = get_doc_or_404('players', player_id)
        status = 200

    return Response(response=json.dumps(response_result),
                    status=status,
                    mimetype='application/json')
