#!flask/bin/python
from flask import Flask, jsonify
from flask_cors import CORS
from flask import abort
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://app_user:mslater@localhost/investing'
db = SQLAlchemy()
db.init_app(app)

class Investment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(), unique=True)
	unitPrice = db.Column(db.Number())
	exchange = db.Column(db.String())

	def __init__(self, symbol, unitPrice, exchange):
		self.symbol = symbol
		self.unitPrice = unitPrice
		self.exchange = exchange

	def __repr__(self):
		return '<Investment %r>' % self.symbol

"""
Here lies the API CRUD operations
"""

def makeJson(investment):
	return {
		'id': investment.id,
		'type': 'investment',
		'attributes': {
			'symbol': investment.symbol,
			'unit-price': investment.unitPrice,
			'exchange': investment.exchange
		}
	}

@app.route('/api/investments', methods=['GET'])
def get_investments():
	investments = Investment.query.all()
	return jsonify({ 'data': map(makeJson, investments) })

@app.route('/api/investments/<int:investment_id>', methods=['GET'])
def get_investment(investment_id):
	investment = Investment.query.filter_by(id=investment_id).first()
	return jsonify({ 'data': makeJson(investment) })

@app.route('/api/investments/<int:investment_id>', methods=['PUT'])
def update_investment(investment_id):

@app.route('/api/investments/', methods=['POST'])
def create_investment():

@app.route('/api/investments/<int:investment_id>', methods=['DELETE'])
def delete_investment(investment_id):
	Investment.delete.fil

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)