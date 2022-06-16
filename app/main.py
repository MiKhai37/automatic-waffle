from flask import Flask, request, json, Response
from flask_cors import CORS, cross_origin
from MongoAPI import MongoAPI
import uuid

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
@cross_origin(supports_credentials=True)
def base():
  return Response(response=json.dumps({"Status": "UP"}),
                  status=200,
                  mimetype='application/json')


@app.route('/games/all', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readAllGames():
  data = request.json
  data['collection']='games'
  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.read()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/get', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_readGame():
  data = request.json
  data['collection']='games'
  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.readOne()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')
initialTiles = [
  {'letter': 'A', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 0}},
  {'letter': 'B', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 1}},
  {'letter': 'C', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 2}},
  {'letter': 'D', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 3}},
  {'letter': 'E', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 4}},
  {'letter': 'F', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 5}},
  {'letter': 'G', 'isSelected': False, 'id': str(uuid.uuid4()), 'isLocked': False, 'location': { 'place': 'rack', 'coords': 6}}
];

@app.route('/games/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_writeGame():
  data = request.json
  data['collection']='games'
  if data is None or data == {} or 'Document' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  data['Document']['tiles'] = initialTiles
  response = obj1.write(data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/update', methods=['PUT'])
@cross_origin(supports_credentials=True)
def mongo_updateGame():
  data = request.json
  data['collection']='games'
  if data is None or data == {} or 'DataToBeUpdated' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.update()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/games/delete', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def mongo_deleteGame():
  data = request.json
  data['collection']='games'
  if data is None or data == {} or 'Filter' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.delete(data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

#if __name__ == '__main__':
#  app.run(debug=False, port=5001, host='0.0.0.0')