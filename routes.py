from flask import json, Response

def base():
 return Response(response=json.dumps({"Status": "UP"}),
                 status=200,
                 mimetype='application/json')