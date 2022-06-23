from flask import Blueprint, request, jsonify, make_response

app = Blueprint('part_time_jobs', __name__)

@app.route("/", methods=['GET'])
def getPartTimeJobs():
    params = request.args
    response = {}
    return make_response(params)

@app.route("/<int:id>", methods=['PATCH'])
def updatePartTimeJobs(id):
    params = request.json
    response = {}
    response.setdefault('id', str(id))
    response.setdefault('params', params)
    return make_response(jsonify(response))

@app.route("/<int:id>", methods=['DELETE'])
def deletePartTimeJobs(id):
    params = request.args
    response = {}
    response.setdefault('id', str(id))
    response.setdefault('params', params)
    return make_response(jsonify(response))

@app.route("/", methods=['POST'])
def createPartTimeJobs():
    params = request.json
    response = {}
    return make_response(params)
