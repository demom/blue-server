import json
import falcon
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError,RqlDriverError
from .db import Db


class ObjectBase:
	TABLE = ""
	STRUCTURE = {}
	db = Db()
	original = dict()
	changed = dict()
	result = dict()

	def __init__(self):
		self.setup_database()

	# Data getter/setters

	def set_property(self, name, value):
		if not name in self.STRUCTURE:
			#raise KeyError()
			return ""

		self.changed[name] = value
	
	def get_property(self, name):
		if not name in self.STRUCTURE:
			#raise KeyError()
			return ""

		if name in self.changed:
			return self.changed[name]
		elif name in self.original:
			return self.original[name]
		
		return ""
	
	#def __setattr__(self, name, value):
	#	self.set_property_value(name, value)
	
	#def __getattr__(self, name):
	#	return self.get_property_value(name)

	# Basic object methods

	def create(self):
		self.original = dict()
		self.changed = dict()
		self.result = dict()

	def open(self, id):
		rawjson = r.db(self.db.PROJECT_DB).table(self.TABLE). get(id).run(self.db.connection)

		if rawjson is None:
			return False

		self.load_from_database(rawjson)
		self.changed = self.original
		return True

	def save(self):
		if "id" in self.original:
			""" Update existing entry """
			self.result = r.db(self.db.PROJECT_DB).table(self.TABLE).filter(r.row["id"] == self.original["id"]).update(self.changed).run(self.db.connection)
		else:
			""" This is a new entry """
			self.result = r.db(self.db.PROJECT_DB).table(self.TABLE).insert(self.changed).run(self.db.connection)

	def delete(self):
		""" Update existing entry """
		self.result = r.db(self.db.PROJECT_DB).table(self.TABLE).filter(r.row["id"] == self.original["id"]).delete().run(self.db.connection)

	# Load data members

	def load_from_json(self, jsondata):
		for key in self.STRUCTURE:
			if key in jsondata:
				self.changed[key] = jsondata[key]

	def load_from_database(self, jsondata):
		for key in self.STRUCTURE:
			if key in jsondata:
				self.original[key] = jsondata[key]

	# HTTP methods

	def on_get(self, req, resp):
		self.request = req
		self.response = resp

		if self.request.get_param("id"):
			if self.open(self.request.get_param("id")):
				self.set_json(self.original)
			else:
				raise falcon.HTTPError(falcon.HTTP_404, 'Object not found', 'Object %s could not be opened' % self.request.get_param("id"))
		else:
			note_cursor = r.db(self.db.PROJECT_DB).table(self.TABLE).run(self.db.connection)
			result = [i for i in note_cursor]
			self.set_json(result)

	def on_post(self, req, resp):
		self.request = req
		self.response = resp

		jsondata = self.get_json()

		self.create()
		self.load_from_json(jsondata)
		self.save()

		self.set_json(self.result)


	def on_put(self, req, resp):
		self.request = req
		self.response = resp

		jsondata = self.get_json()

		if "id" in jsondata:
			if self.open(jsondata["id"]):
				self.load_from_json(jsondata)
				self.save()

				self.set_json(self.result)
			else:
				raise falcon.HTTPError(falcon.HTTP_404, 'Object not found', 'Object %s could not be opened' % jsondata["id"])
		else:
			raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'The JSON document lacked an ID field')


	def on_delete(self, req, resp):
		self.request = req
		self.response = resp

		jsondata = self.get_json()

		if "id" in jsondata:
			if self.open(jsondata["id"]):
				self.delete()

				self.set_json(self.result)
			else:
				raise falcon.HTTPError(falcon.HTTP_404, 'Object not found', 'Object %s could not be opened' % jsondata["id"])
		else:
			raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'The JSON document lacked an ID field')

	# Setup members

	def setup_database(self):
		try:
			r.db(self.db.PROJECT_DB).table_create(self.TABLE).run(self.connection)
			print("Table %s created" % self.TABLE)
		except:
			print("Table %s verified" % self.TABLE)

	# To / from JSON

	def get_json(self):
		try:
			raw_json = self.request.stream.read()
		except Exception as ex:
			raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

		try:
			result = json.loads(raw_json.decode('utf-8'))
		except ValueError:
			raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The JSON was incorrect.')

		return result

	def set_json(self, jsondata):
		self.response.body = json.dumps(jsondata)
