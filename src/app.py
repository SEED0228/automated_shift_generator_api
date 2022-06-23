# coding: utf-8
from flask import Flask, request, jsonify, make_response
from api.v1 import part_time_jobs
from api.v1 import test
app = Flask(__name__)
app.register_blueprint(part_time_jobs.app, url_prefix='/api/v1/part_time_jobs')
app.register_blueprint(test.app, url_prefix='/api/v1/test')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)