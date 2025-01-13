from flask import Flask
"""
The Flask class is the main class of the Flask framework. 
An instance of this class will be our WSGI application.
"""
app = Flask(__name__)

@app.route("/")
def welcome():
    return "Welcome to the Flask World!"

@app.route("/index")
def index():
    return "This is the index page!"

if __name__ == "__main__":
    app.run(debug = True)