from myqueue import init_db

def initdb_command():
	'''Creates the database tables.'''
	init_db()
	print('Initialized the database.')

def init_db():
    '''Initializes the database.'''
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

if '__name__' == '__main__':
	initdb_command()