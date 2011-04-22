from website import app

@app.route("/hello")
def hello():
    return "Hello, World!"
