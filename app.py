from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
import bcrypt
import os
from werkzeug.utils import secure_filename
import cloud
import speechToText
import sumy

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
  return render_template('login.html')

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            gcs_uploader = cloud.Cloud()
            gcs_uploader.upload_blob("sumy",'{}/{}'.format(app.config['UPLOAD_FOLDER'],filename),filename)
            return redirect(url_for('dashboard',
                                    filename=filename))
    return render_template('upload.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # check if the post request has the file part
        #This part should have the data

        #Saving to a temporary place
        output_string = speechToText.generate_analysis('sumy',request.form['filename'])
        with open("./textfiles/temp.txt","w+") as f:
            f.write(output_string)

        #Reading and cleaning
        content = sumy.read_file("./static/textfiles/temp.txt")
        content = sumy.sanitize_input(content)

        #Tokenizing and summarizing
        sentence_tokens, word_tokens = sumy.tokenize_content(content)
        sentence_ranks = sumy.score_tokens(word_tokens, sentence_tokens)
        output_summary = sumy.summarize(sentence_ranks, sentence_tokens, 3)
        with open("./static/textfiles/summary.txt","w+") as f:
            f.write(output_summary)

        #Written to a textfile

        return redirect(url_for('dashboard'))
    return render_template('analyze.html')

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run('0.0.0.0',debug=True)
