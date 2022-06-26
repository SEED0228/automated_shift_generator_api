from flask import Blueprint, request, jsonify, make_response, current_app
from mongo import get_mongo_client
from bson.json_util import dumps
import json
from uuid import uuid4
from datetime import datetime

app = Blueprint('part_time_jobs', __name__)

@app.route("/", methods=['GET'])
def getPartTimeJobs():
    client = get_mongo_client()
    user = client.test.users.find_one()
    params = request.args
    response = {}
    response.setdefault('status', 200)
    response.setdefault('part_time_jobs', user['part_time_jobs'] if 'part_time_jobs' in user else {})
    return make_response(jsonify(response))

@app.route("/<string:id>", methods=['PATCH'])
def updatePartTimeJobs(id):
    client = get_mongo_client()
    user = json.loads(dumps(client.test.users.find_one()))
    response = {}
    params = request.json
    part_time_job = list(filter(lambda part_time_job: part_time_job['id'] == id, user['part_time_jobs']))
    if len(part_time_job) == 1:
        current_app.logger.info(part_time_job)
        params['id'] = part_time_job[0]['id']
        params['created_at'] = part_time_job[0]['created_at']
        client.test.users.update_one(
            {
                'name':user['name']
            },
            {
                '$set': {
                    'part_time_jobs.$[element]': params
                }
            },
            upsert=True,
            array_filters=[ { 'element.id': id } ]
        )
        response.setdefault('status', 200)
        user = json.loads(dumps(client.test.users.find_one()))
    else:
        response.setdefault('status', 203)
    response.setdefault('part_time_jobs', user['part_time_jobs'] if 'part_time_jobs' in user else {})
    return make_response(jsonify(response))

@app.route("/<string:id>", methods=['DELETE'])
def deletePartTimeJobs(id):
    client = get_mongo_client()
    params = request.args
    user = client.test.users.find_one()
    client.test.users.update_one(
        {
            'name': user['name']
        },
        {
            '$pull': {
                'part_time_jobs': { 'id': id }
            }
        }
    )
    user = json.loads(dumps(client.test.users.find_one()))
    response = {}
    response.setdefault('status', 200)
    response.setdefault('part_time_jobs', user['part_time_jobs'] if 'part_time_jobs' in user else {})
    return make_response(jsonify(response))

@app.route("/", methods=['POST'])
def createPartTimeJobs():
    client = get_mongo_client()
    user = json.loads(dumps(client.test.users.find_one()))
    params = request.json
    params['id'] = str(uuid4())
    params['created_at'] = datetime.now()
    current_app.logger.info(type(params['id']))
    current_app.logger.info(user['name'])
    client.test.users.update_one(
        {
            'name':user['name']
        },
        {'$push': {
                'part_time_jobs': params
            }
        }
    )
    user = json.loads(dumps(client.test.users.find_one()))
    response = {}
    response.setdefault('status', 200)
    response.setdefault('part_time_jobs', user['part_time_jobs'] if 'part_time_jobs' in user else {})
    return make_response(response)
