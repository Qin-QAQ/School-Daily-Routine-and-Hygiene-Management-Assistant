import flask
from flask import Flask, jsonify, request
from flask.sansio.app import App
from flask_cors import CORS
from tool_kit import User

class App(Flask):
    def __init__(self):
        super(App, self).__init__(__name__)
        CORS(self)

        self.add_url_rule('/api/login', view_func=self.login, methods=['GET', 'POST'])

    def login(self):

        return jsonify({'code': 200})

if __name__ == '__main__':
    app = App()
    app.run(debug=True)