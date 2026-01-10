import json
from flask import Flask, jsonify, request
from flask_cors import CORS

from tool_kit import User


app = Flask(__name__)
CORS(app)
def response(text):
    return jsonify({"code": 200, "message": text})

def json_to_dict(json_string):
    return json.loads(json_string)
def check_level(name, pwd, level):
    u = User(login_name=name, password=pwd)
    if u.login_level != level:
        return False
    return True


@app.route('/api/get-login-level')
def login():
    password = request.args.get('password')
    name = request.args.get('name')
    print("OK")
    print(password)
    print(name)
    u = User(login_name=name, password=password)
    return response(u.login_level)
@app.route('/api/')
@app.route('/api/test')
def test():
    return jsonify({"code": 200, "message": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)




























