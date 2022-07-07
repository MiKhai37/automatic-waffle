from flask import abort
from flask_app.db import get_mongo_db


def get_body_or_400(request, req_params, opt_params=None):
    if opt_params is None:
        opt_params = []
    body = request.json
    if any(param not in body for param in req_params):
        abort(
            400, description=f'Missing parameters in body, required parameters: {req_params}'
        )
    elif any(param not in req_params + opt_params for param in body):
        abort(
            400, description=f'Unneeded parameter in body, possible parameters: {req_params + opt_params}'
        )
    else:
        return body


def get_n_docs(collection, n):
    collection_api = get_mongo_db(collection)
    return collection_api.read_many_docs(n)


def delete_doc_or_404(collection, doc_id, id_key='id'):
    coll_api = get_mongo_db(collection)
    delete_result = coll_api.delete_doc({id_key: doc_id})
    if (delete_result['Status'] == 'Document not found'):
        abort(404, 'Document not found')
    return delete_result


def get_doc_or_404(collection, doc_id, id_key='id'):
    coll_api = get_mongo_db(collection)
    doc = coll_api.read_one_doc({id_key: doc_id})
    if(doc is None):
        abort(
            404, description=f'Document {id_key}: {doc_id} not found in collection: {collection}')
    return doc
