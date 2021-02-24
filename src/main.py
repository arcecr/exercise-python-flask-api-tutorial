"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, redirect
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Todo
import json


app = Flask(__name__)

app.url_map.strict_slashes = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)

CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Redirect to API Docs 
@app.route('/')
def home():
    return redirect("/api/docs", code=302)

# Return all todos
@app.route('/todos', methods=['GET'])
def getTodos():

    query = Todo.query.all()

    results = list(map(lambda x: x.serialize(), query))

    return jsonify(results), 200


# Add todo
@app.route('/todos', methods=['POST'])
def addTodo():
    
    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=405)

    label = request.json.get("label", None)

    if not label:
        raise APIException('Missing label parameter', status_code=405)
    
    todo = Todo()
    todo.label = label

    db.session.add(todo)
    db.session.commit()

    return jsonify("Successful operation"), 200


# Update todo by id
@app.route('/todos/<int:tid>', methods=['PUT'])
def updateTodo(tid):

    todo = Todo.query.get(tid)

    if todo is None:
        raise APIException('Task not found', status_code=404)

    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=405)

    label = request.json.get("label", None)
    done = request.json.get("done", None)

    if label is None or done is None:
        raise APIException('Missing label or done parameter', status_code=405)

    todo.label = label
    todo.done = done

    db.session.commit()

    results = list(map(lambda x: x.serialize(), Todo.query.all()))

    return jsonify(results), 200


# Delete todo by id
@app.route('/todos/<int:tid>', methods=['DELETE'])
def deleteTodo(tid):

    todo = Todo.query.get(tid)

    if todo is None:
        return jsonify("Task not found"), 404

    db.session.delete(todo)
    db.session.commit()

    results = list(map(lambda x: x.serialize(), Todo.query.all()))

    return jsonify(results), 200

# Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    '/api/docs', 
    "/static/swagger.json",
    config = {  
        'app_name': "Todo Application"
    },
)

app.register_blueprint(swaggerui_blueprint)


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
