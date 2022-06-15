from flask import Flask, request, json, Response
from flask_cors import CORS, cross_origin
from MongoAPI import MongoAPI

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
@cross_origin(supports_credentials=True)
def base():
  return Response(response=json.dumps({"Status": "UP"}),
                  status=200,
                  mimetype='application/json')


@app.route('/games/all', methods=['GET'])
@cross_origin(supports_credentials=True)
def mongo_read():
  data = request.json
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
def mongo_readOne():
  data = request.json
  if data is None or data == {}:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.readOne()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/mongodb', methods=['POST'])
@cross_origin(supports_credentials=True)
def mongo_write():
  data = request.json
  if data is None or data == {} or 'Document' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.write(data)
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/mongodb', methods=['PUT'])
@cross_origin(supports_credentials=True)
def mongo_update():
  data = request.json
  if data is None or data == {} or 'DataToBeUpdated' not in data:
    return Response(response=json.dumps({"Error": "Please provide connection information"}),
                    status=400,
                    mimetype='application/json')
  obj1 = MongoAPI(data)
  response = obj1.update()
  return Response(response=json.dumps(response),
                  status=200,
                  mimetype='application/json')

@app.route('/mongodb', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def mongo_delete():
  data = request.json
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