import uuid
from datetime import datetime, timezone

from flask import Blueprint, Response, json, request

from .mongo_api import MongoAPI
from .request_helpers import (delete_doc_or_403, get_body_or_400,
                              get_doc_or_404, get_n_docs)

bp = Blueprint('game', __name__, url_prefix='/game')