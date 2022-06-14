from flask import Flask, request, json, Response
from MongoAPI import MongoAPI

app = Flask(__name__)

@app.route('/')
def base():
  return Response(response=json.dumps({"Status": "UP"}),
                  status=200,
                  mimetype='application/json')


@app.route('/mongodb', methods=['GET'])
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


@app.route('/mongodb', methods=['POST'])
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