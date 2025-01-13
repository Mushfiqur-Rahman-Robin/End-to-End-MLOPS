from flask import Flask, render_template, request, redirect, url_for
"""
The Flask class is the main class of the Flask framework. 
An instance of this class will be our WSGI application.
{{ }} is used to print the value of a variable.
{{ %..% }} is used to execute the control statements.
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

# @app.route("/submit", methods = ["GET", "POST"])
# def submit():
#     if request.method == "POST":
#         name = request.form.get("name")
#         return f"Hello {name}!"
    
#     return render_template("form.html")


# variable rule
@app.route("/success/<int:score>", methods = ["GET", "POST"])
def success(score):
    res = ""
    if score >= 50:
        res = "pass"
    else:
        res = "fail"

    return render_template("result.html", result = res)

@app.route("/res_condition/<int:score>")
def res_condition(score):
    res = ""
    if score >= 50:
        res = "pass"
    else:
        res = "fail"
    
    exp = {"score": score, "res": res}

    return render_template("result_condition.html", result = exp)

@app.route("/successif/<int:score>")
def successif(score):
    return render_template("result.html", result = score)


@app.route("/fail/<int:score>", methods = ["GET", "POST"])
def fail(score):
    return render_template("result.html", result = score)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        science = int(request.form.get("science", 0))
        maths = int(request.form.get("maths", 0))
        c = int(request.form.get("c", 0))
        datascience = int(request.form.get("datascience", 0))

        total_mean_score = (science + maths + c + datascience) / 4
    
    else:
        return render_template("getresult.html")

    return redirect(url_for("res_condition", score=int(total_mean_score)))


if __name__ == "__main__":
    app.run(debug = True)