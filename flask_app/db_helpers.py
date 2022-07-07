from flask import abort
from flask_app.db import get_mongo_db


def get_body_or_400(request, req_params):
    body = request.json
    if body.keys() != set(req_params):
        abort(
            400, description=f'Missing parameters in body, required parameters: {req_params}')
    else:
        return body


def get_n_docs(collection, n):
    collection_api = get_mongo_db(collection)
    return collection_api.read_many_docs(n)


def delete_doc_or_403(collection, doc_id, id_key='id'):
    coll_api = get_mongo_db(collection)
    if ('Test' in doc_id):
        abort(403, 'Deletion of testing docs is unallowed')
    return coll_api.delete_doc({id_key: doc_id})


def get_doc_or_404(collection, doc_id, id_key='id'):
    coll_api = get_mongo_db(collection)
    doc = coll_api.read_one_doc({id_key: doc_id})
    if(doc is None):
        abort(
            404, description=f'Document {id_key}: {doc_id} not found in collection: {collection}')
    return doc