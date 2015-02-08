from myqueue import init_db

def initdb_command():
	'''Creates the database tables.'''
	init_db()
	print('Initialized the database.')
	
if '__name__' == '__main__':
	initdb_command()