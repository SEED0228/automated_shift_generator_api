# coding: utf-8
from flask import Flask, request, jsonify, make_response
from api.v1 import part_time_jobs, test, users, shifts
app = Flask(__name__)
app.register_blueprint(part_time_jobs.app, url_prefix='/api/v1/part_time_jobs')
app.register_blueprint(test.app, url_prefix='/api/v1/test')
app.register_blueprint(users.app, url_prefix='/api/v1/users')
app.register_blueprint(shifts.app, url_prefix='/api/v1/shifts')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)