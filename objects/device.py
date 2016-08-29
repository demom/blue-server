from framework.api import api
from framework.object import ObjectBase


class Device (ObjectBase):

	TABLE = "Device"
	STRUCTURE = {
		"id": {"type": "guid"},
		"name": {"type": "string"},
		"type": {"type": "string"},
		"vendor": {"type": "string"}
	}

	@property
	def id(self):
		return self.get_property("id")
	
	@id.setter
	def id(self, value):
		self.set_property("id", value)

	@property
	def name(self):
		return self.get_property("name")
	
	@name.setter
	def name(self, value):
		self.set_property("name", value)

api.add_route('/api/v1/object/device', Device())
