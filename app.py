from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME']='landan'
app.config['MONGO_URI']='mongodb://check:cheeky1@ds026898.mlab.com:26898/landan'

mongo = PyMongo(app)

bootstrap = Bootstrap()
bootstrap.init_app(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "THISISSECRET"

mongo = PyMongo(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass })
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return render_template('signup.html', error = "That username is already taken")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user:
            print(request.form['pass'].encode('utf-8'))
            print(login_user['password'])
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                session['logged_in']=True

                return redirect(url_for('dashboard'))

        return 'Invalid username/password combination'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    session['logged_in']=False
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
  return render_template('dashboard.html', name=session['username'])

@app.route('/about')
def about():
  return render_template('about.html')


if __name__ == '__main__':
  app.run('0.0.0.0',debug=True)
