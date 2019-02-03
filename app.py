from flask import Flask, render_template, url_for, request, session, redirect
from flask_bootstrap import Bootstrap

app = Flask(__name__)

bootstrap = Bootstrap()
bootstrap.init_app(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/summarize')
def summarize():
  return render_template('summarize.html')

@app.route('/about')
def about():
  return render_template('about.html')


if __name__ == '__main__':
  app.run('0.0.0.0',debug=True)
