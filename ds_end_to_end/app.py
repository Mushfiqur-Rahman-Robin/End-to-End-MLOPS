from flask import Flask, render_template, request
import os
import numpy as np
import pandas as pd
from src.ds_end_to_end.pipeline.prediction_pipe import PredictionPipeline

app = Flask(__name__)

@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")

@app.route("/train", methods=["GET"])
def train():
    os.system("python main.py")
    return "Training successful!"

@app.route("/predict", methods=["POST", "GET"])
def predict():
    if request.method == "POST":
        try:
            fixed_acidity = float(request.form.get("fixed_acidity"))
            volatile_acidity = float(request.form.get("volatile_acidity"))
            citric_acid = float(request.form.get("citric_acid"))
            residual_sugar = float(request.form.get("residual_sugar"))
            chlorides = float(request.form.get("chlorides"))
            free_sulfur_dioxide = float(request.form.get("free_sulfur_dioxide"))
            total_sulfur_dioxide = float(request.form.get("total_sulfur_dioxide"))
            density = float(request.form.get("density"))
            pH = float(request.form.get("pH"))
            sulphates = float(request.form.get("sulphates"))
            alcohol = float(request.form.get("alcohol"))

            data = [
                fixed_acidity,
                volatile_acidity,
                citric_acid,
                residual_sugar,
                chlorides,
                free_sulfur_dioxide,
                total_sulfur_dioxide,
                density,
                pH,
                sulphates,
                alcohol
            ]

            data = np.array(data).reshape(1, -1)
            pipeline = PredictionPipeline()
            prediction = pipeline.predict(data)

            return render_template("results.html", prediction=str(prediction[0]))

        except Exception as e:
            print(e)
            return "Something went wrong!"
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)