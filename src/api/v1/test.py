from flask import Blueprint, request, jsonify, make_response, current_app
from mongo import get_mongo_client
from bson.json_util import dumps
import json

app = Blueprint('test', __name__)

@app.route("/", methods=['GET'])
def test():
    params = request.args
    current_app.logger.info('info')
    response = {}
    client = get_mongo_client()
    user = client['test'].get_collection('users').find_one()
    if user:
        response.setdefault('status', 200)
        response.setdefault('user', json.loads(dumps(user)))
    else:
        response.setdefault('status', 204)
    return make_response(jsonify(response))