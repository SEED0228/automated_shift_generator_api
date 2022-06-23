from flask import Blueprint, request, jsonify, make_response
from mongo import get_mongo_client

app = Blueprint('test', __name__)

@app.route("/", methods=['GET'])
def getPartTimeJobs():
    params = request.args
    response = {}
    client = get_mongo_client()
    user = client['test'].get_collection('users').find_one()
    del user["_id"]
    return make_response(user)