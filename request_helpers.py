from flask import json, Response, abort
from MongoAPI import MongoAPI


def get_body_or_400(request, req_params):
    body = request.json
    if any(prop not in body for prop in req_params):
        abort(
            400, description=f'Missing parameters in body, required parameters: {req_params}')
    else:
        return body


def get_n_docs(collection, n):
    collection_api = MongoAPI(collection)
    return collection_api.read_many_docs(n)


def delete_doc_or_403(collection, doc_id, id_key='id'):
    coll_api = MongoAPI(collection)
    if ('Test' in doc_id):
        abort(403, 'Deletion of testing docs is unallowed')
    return coll_api.delete_doc({id_key: doc_id})


def get_doc_or_404(collection, doc_id, id_key='id'):
    coll_api = MongoAPI(collection)
    doc = coll_api.read_one_doc({id_key: doc_id})
    if(doc.get('Code') == 404):
        abort(
            404, description=f'Document {id_key}: {doc_id} not found in collection: {collection}')
    return doc
