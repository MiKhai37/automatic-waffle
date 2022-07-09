from datetime import datetime, timezone
from turtle import update
from uuid import uuid4

from flask import Blueprint, Response, abort, json, request
from flask_app.db import get_mongo_db

from scrabble_python import Scrabble

from flask_app.db_helpers import (delete_doc_or_404, get_body_or_400,
                              get_doc_or_404, get_n_docs)

bp = Blueprint('play', __name__, url_prefix='/play')