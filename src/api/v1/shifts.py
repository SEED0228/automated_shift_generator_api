from flask import Blueprint, request, jsonify, make_response, current_app
from mongo import get_mongo_client
from bson.json_util import dumps
import json
from uuid import uuid4
from datetime import datetime
from modules.create_shifts import create_shifts

app = Blueprint('shifts', __name__)

@app.route("/create", methods=['POST'])
def createShifts():
    client = get_mongo_client()
    user = json.loads(dumps(client.test.users.find_one()))
    params = request.json
    response = {}
    part_time_jobs = user['part_time_jobs'] if 'part_time_jobs' in user else []
    if len(part_time_jobs) >= 1:
        result = create_shifts(part_time_jobs, params)
        response.setdefault('status', 200)
        response.setdefault('data', result)
    else:
        response.setdefault('status', 203)
    response.setdefault('params', params)
    return make_response(response)