from flask_sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app)

class BaseModel(object):
	@classmethod
	def delete(cls, id):
		db.session.query(cls).filter_by(id=id).delete()
		db.session.commit()

	@classmethod
	def create(cls, **kwargs):
		instance = cls(**kwargs)
		db.session.add(instance)
		db.session.commit()
		return instance

	@classmethod
	def update(cls, **kwargs):
		db.session.query(cls).filter_by(id=kwargs['id']).update(kwargs)
		db.session.commit()
		return db.session.query(cls).filter_by(id=kwargs['id']).first()

	@classmethod
	def retrieve(cls, id):
		return db.session.query(cls).filter_by(id=id).first()

	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			if not attr == 'id' and not attr.startswith('_'):
				yield attr, value


class User(db.Model, BaseModel):
	__tablename__ = 'users'

	id = db.Column(db.String(), primary_key=True)
	first_name = db.Column(db.String())
	last_name = db.Column(db.String())

	def __init__(self, **kwargs):
		self.first_name = kwargs['first_name']
		self.last_name = kwargs['last_name']
		self.id = kwargs['id']

	def __repr__(self):
		return '<{} {}>'.format(self.first_name, self.last_name)