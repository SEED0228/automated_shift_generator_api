from flask import Blueprint, request, jsonify, make_response, current_app
from mongo import get_mongo_client
from bson.json_util import dumps
import json
from uuid import uuid4

app = Blueprint('users', __name__)

@app.route("/", methods=['POST'])
def createUsers():
    params = request.json
    params['id'] = str(uuid4())
    current_app.logger.info(params)
    response = {}
    client = get_mongo_client()
    client.test.users.insert_one(params)
    current_app.logger.info(params)
    response.setdefault('status', 200)
    response.setdefault('data', json.loads(dumps(params)))
    return make_response(jsonify(response))
