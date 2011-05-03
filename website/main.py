from flask import render_template
from website import app

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/plugin")
def plugin():
    return render_template('plugin.html')

@app.route("/about")
def about():
    return render_template('about.html')
