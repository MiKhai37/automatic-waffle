import json
import jsonpickle

def obj_to_doc(obj: object) -> dict:
    return json.loads(jsonpickle.encode(obj))

def doc_to_obj(doc: dict) -> object:
    return jsonpickle.decode(json.dumps(doc))

def JSONstr_to_doc(JSONstr: str) -> dict:
    return json.loads(JSONstr)

def JSONstr_to_obj(JSONstr: str) -> object:
    return jsonpickle.decode(JSONstr)

def doc_to_JSONstr(doc: dict) -> str:
    return json.dumps(doc)

def obj_to_JSONstr(obj: object) -> str:
    return jsonpickle.encode(obj)