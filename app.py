#!flask/bin/python
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import abort
from flask import make_response
import uuid

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

CORS(app, resources=r'/api/*')

from models import User

def kebab_case_to_snake_case(string):
	return '_'.join(string.split('-'))

def snake_case_to_kebab_case(string):
	return '-'.join(string.split('_'))

def deserialize(json):
	if not 'data' in json:
		return json
	if not 'attributes' in json['data']:
		return json
	data = json['data']['attributes']
	data['id'] = None if not 'id' in json['data'] else json['data']['id']
	for key in data.keys():
		data[kebab_case_to_snake_case(key)] = data.pop(key)
	return data

def serialize(klass):
	attributes = dict(klass)
	for key in attributes.keys():
		attributes[snake_case_to_kebab_case(key)] = attributes.pop(key)
	data = { 
		'type': str.lower(type(klass).__name__), 
		'id': klass.id, 
		'attributes': attributes
	}
	return data

@app.route('/api/users', methods=['GET'])
def get_users():
	all_users = User.query.all()
	return jsonify({ 'data': map(serialize, all_users) })

@app.route('/api/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
	user = User.retrieve(id=user_id)
	if user == None:
		abort(404)
	return jsonify({ 'data': serialize(user) })

@app.route('/api/users/<string:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
	attrs = deserialize(request.json)
	user = User.update(**attrs)
	if user == None:
		abort(404)
	return jsonify({ 'data': serialize(user) })

@app.route('/api/users', methods=['POST'])
def create_user():
	try:
		attrs = deserialize(request.json)
		attrs['id'] = str(uuid.uuid4())
		saved_user = User.create(**attrs)
		return jsonify({ 'data': serialize(saved_user) })
	except Exception as e:
		return jsonify({ 'error': e })

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
	User.delete(user_id)
	return ('', 204)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)