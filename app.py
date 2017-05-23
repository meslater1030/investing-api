#!flask/bin/python
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import abort
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
import logging
from subprocess import check_call
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.types as sa_types

__all__ = ('Session',
           'init_local_db')

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/investing'
db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.String(), primary_key=True)
	first_name = db.Column(db.String())
	last_name = db.Column(db.String())

	def __init__(self, first_name, last_name, id):
		self.first_name = first_name
		self.last_name = last_name
		self.id = id

	def __repr__(self):
		return '<{} {}>'.format(self.first_name, self.last_name)

def scrub_data(user):
	return {
		'type': 'user',
		'id': user.id,
		'attributes': {
			'first-name': user.first_name,
			'last-name': user.last_name
		}
	}

@app.route('/api/users', methods=['GET'])
def get_users():
	all_users = User.query.all()
	return jsonify({ 'data': map(scrub_data, all_users) })

@app.route('/api/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
	user = db.session.query(User).filter_by(id=user_id).first()
	if len(user) == 0:
		abort(404)
	return jsonify({ 'data': scrub_data(user) })

@app.route('/api/users/<string:user_id>', methods=['PUT'])
@app.route('/api/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
	attrs = {
		'first_name': request.json['data']['attributes']['first-name'],
		'last_name': request.json['data']['attributes']['last-name']
	}
	user = db.session.query(User).filter_by(id=user_id).update(attrs)
	db.session.commit()
	if user == 0:
		abort(404)
	return jsonify({ 'data': {
			'type': 'user',
			'id': user_id,
			'attributes': request.json['data']['attributes']
		} })

@app.route('/api/users', methods=['POST'])
def create_user():
	id = str(uuid.uuid4())
	attrs = {
		'id': id,
		'first_name': request.json['data']['attributes']['first-name'],
		'last_name': request.json['data']['attributes']['last-name']
	}
	user = User(**attrs)
	db.session.add(user)
	db.session.commit()
	saved_user = db.session.query(User).filter_by(id=id).first()
	return jsonify({'data': { 'type': 'user', 'id': saved_user.id, 'attributes': { 'first-name': saved_user.first_name, 'last-name': saved_user.last_name }}})

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
	db.session.query(User).filter_by(id=user_id).delete()
	db.session.commit()
	return ('', 204)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)