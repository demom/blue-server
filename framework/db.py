import os
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

class Db:

	RDB_HOST = 'localhost'
	RDB_PORT = 28015
	PROJECT_DB = 'Aurora'
	PROJECT_TABLE = 'Inventory'
	connection = r.connect(RDB_HOST, RDB_PORT)


	# Function is for cross-checking database and table exists
	def Setup(self):
		try:
			r.db_create(self.PROJECT_DB).run(self.connection)
			print("Database setup completed.")
		except RqlRuntimeError:
			print("Database already exists. Nothing to do")

		try:
			r.db(self.PROJECT_DB).table_create(self.PROJECT_TABLE).run(self.connection)
			print("Table creation completed")
		except:
			print("Table already exists. Nothing to do")
