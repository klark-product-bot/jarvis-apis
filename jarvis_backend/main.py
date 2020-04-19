from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from admin_panel_resources import signup, login
import mongoengine

app = Flask(__name__)
cors = CORS(app)
api = Api(app)


mongoengine.connect('Jarvis')

class Signup(Resource):
    def post(self):
        resp = signup(request.get_json())
        return jsonify(resp)

class Login(Resource):
    def post(self):
        resp = login(request.get_json())
        return jsonify(resp)

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")

if __name__ == "__main__":
    app.run(port=5000, debug=True)