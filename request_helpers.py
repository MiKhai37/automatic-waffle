from flask import json, Response, abort

from MongoAPI import MongoAPI


def get_body_or_400(request, req_params):
    body = request.json
    if any(prop not in body for prop in req_params):
        abort(
            400, f'Missing parameters in body, required parameters: {req_params}')
    else:
        return body


def get_n_docs(collection, n):
    collection_api = MongoAPI(collection)
    collection_docs = collection_api.read_many_docs(n)
    return Response(response=json.dumps(collection_docs),
                    status=200,
                    mimetype='application/json')


def get_or_delete_doc(method, collection, doc_id):
    coll_api = MongoAPI(collection)
    if method == 'GET':
        doc = coll_api.read_one_doc({'id': doc_id})
        if(doc.get('Code') == 404):
            abort(404, f'{collection} document not found')
        return Response(response=json.dumps(doc),
                        status=200,
                        mimetype='application/json')
    if method == 'DELETE':
        if ('Test' in doc_id):
            abort(403, 'Deletion of testing docs is unallowed')
        delete_result = coll_api.delete_doc({'id': doc_id})
        return Response(response=json.dumps(delete_result),
                        status=delete_result['Code'],
                        mimetype='application/json')

def get_doc_or_404(collection, doc_id, id_key='id'):
    coll_api = MongoAPI(collection)
    doc = coll_api.read_one_doc({id_key: doc_id})
    if(doc.get('Code') == 404):
        abort(404, f'{collection} document not found')
    return doc

