from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, url_for, redirect, \
    render_template, g, _app_ctx_stack
app = Flask(__name__)

DATABASE = '/tmp/myqueue.db'
PER_PAGE = 30

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    '''Opens a new database connection if there is non yet for the
    current application context.
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    '''Initializes the database.'''
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    '''Queries the database and returns a list of dictionaries.'''
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def get_user_id(username):
    '''Convenience method to look up the id for a username.'''
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                        [session['user_id']], one=True)

@app.route('/')
def homepage():
    '''Show a user's saved articles in Queue or if no user is logged in it
    will redirect to the sign-in page.
    '''

    if not g.user:
        return redirect(url_for('public_queues'))
    return render_template('my_queue.html', messages=query_db('''
        select article.*, user.* from article, user
        where article.author_id = user.user_id and
            user.user_id = ?
        order by article.post_date desc limit ?''',
        [session['user_id'], PER_PAGE]))

@app.route('/public')
def public_queues():
    """Displays the top public queues from all users."""
    return render_template('my_queue.html', messages=query_db('''
        select article.*, user.* from article, user
        where article.author_id = user.user_id
        order by article.post_date desc limit ?''', [PER_PAGE]))



@app.route('/login')
def login():
    html = """
        <h1>Welcome yo <b>Your</b> Queue</h1>
        <br><br><br><br><br>
        <h2>This is the right place to store interesting stuff you'd want to read later</h2>
        <br><br><br><br>
        <center>
            <form action="login.js" method="POST">
            <fieldset>
            <legend>Sign In</legend>
                Username: <input type="text" name="username">
                <br>
                Password: <input type="text" name="password">
                <br><br>
                <input type="submit" value="Submit">
            </fieldset>
            </form>
        </center>
        <p>Not a member yet? Register now and start manage your online activities like you never did!

    """
    return html

if __name__ == '__main__':
    app.run(debug=True)