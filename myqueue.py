import time
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, url_for, redirect, \
    render_template, g, _app_ctx_stack, flash
from werkzeug import check_password_hash, generate_password_hash
import logging

app = Flask(__name__, static_url_path = "/static", static_folder = "static")

DATABASE = 'myqueue.db'
PER_PAGE = 30
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
    '''Opens a new database connection if there is non yet for the
    current application context.
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# @app.cli.command('initdb')
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

def thumbnail_path(url):
    return 'static/under-construction.jpg'

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                        [session['user_id']], one=True)

@app.route('/')
def homepage():
    '''Show a user's saved bookmarks in Queue or if no user is logged in it
    will redirect to the sign-in page.
    '''

    if not g.user:
        return redirect(url_for('login'))
    return render_template('homepage.html', bookmarks=query_db('''
        select bookmark.*, user.* from bookmark, user
        where bookmark.author_id = user.user_id and
            user.user_id = ?
        order by bookmark.post_date desc limit ?''',
        [session['user_id'], PER_PAGE]))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('homepage'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username= ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            # flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('homepage'))

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('homepage'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into user (
                username, email, pw_hash) values(?, ?, ?)''',
                [request.form['username'],request.form['email'],
                generate_password_hash(request.form['password'])])
            db.commit()
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('user_id', None)
    return render_template('logout.html')


@app.route('/add_bookmark', methods=['POST'])
def add_bookmark():
    """Registers a new bookmark for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['url']:
        db = get_db()
        app.logger.debug(" entered url:"+ request.form['url'] +
                            " desc:" + request.form['desc'])
        db.execute('''insert into bookmark (author_id, url, name, post_date,
            thumb_file_path) values (?, ?, ?, ?, ?)''',
            [session['user_id'], request.form['url'], request.form['desc'],
            int(time.time()), thumbnail_path(request.form['url'])])
        db.commit()
        flash('Your bookmark was added.')
    return redirect(url_for('homepage'))

app.jinja_env.filters['datetimeformat'] = format_datetime

@app.route('/del_bookmark/<bookmark_id>', methods=['GET'])
def del_bookmark(bookmark_id):
    "Removes a bookmark from user's bookmarks list"
    if 'user_id' not in session:
        abort(401)
    db = get_db()
    app.logger.debug(" deleteing record with id=" + bookmark_id)
    db.execute("delete from bookmark where bookmark_id=? and author_id=?",
            [bookmark_id, session['user_id']])
    db.commit()
    flash("Bookmark deleted")
    return redirect(url_for('homepage'))


app.jinja_env.filters['datetimeformat'] = format_datetime

if __name__ == '__main__':
    app.run(debug=True)