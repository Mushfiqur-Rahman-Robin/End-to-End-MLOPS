from flask import Flask, render_template, request
"""
The Flask class is the main class of the Flask framework. 
An instance of this class will be our WSGI application.
"""
app = Flask(__name__)

@app.route("/")
def welcome():
    return "<html><h1>Welcome to the Flask World!</h1><html>"

@app.route("/index", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/form", methods = ["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        return f"Hello {name}!"
    
    return render_template("form.html")

@app.route("/submit", methods = ["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form.get("name")
        return f"Hello {name}!"
    
    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug = True)