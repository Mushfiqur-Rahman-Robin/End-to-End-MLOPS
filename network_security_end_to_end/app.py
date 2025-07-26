import sys
import os
import pymongo
import pandas as pd

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME, DATA_INGESTION_COLLECTION_NAME, TARGET_COLUMN
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()

username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD")

uri = f"mongodb+srv://{username}:{password}@cluster0.ywc3jur.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = pymongo.MongoClient(uri, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="./templates")

@app.get("/", tags = ["Authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train", tags = ["Train"])
async def train_route():
    try:
        training_pipeline = TrainingPipeline()
        training_pipeline.run_pipeline()
        return Response("Training successful!")
    except Exception as e:
        logging.error(f"Error during training pipeline: {e}", exc_info=True)
        raise NetworkSecurityException(e, sys)
    
@app.post("/predict", tags = ["Predict"])
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        logging.info(f"Received file: {file.filename}, Content-Type: {file.content_type}")

        if not file.filename.lower().endswith(".csv"):
            logging.error(f"Invalid file type uploaded: {file.filename}")
            raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

        df = pd.read_csv(file.file)

        PREPROCESSOR_PATH = "final_models/preprocessor.pkl"
        MODEL_PATH = "final_models/model.pkl"

        if not os.path.exists(PREPROCESSOR_PATH):
            logging.error(f"Preprocessor file not found at: {PREPROCESSOR_PATH}")
            raise HTTPException(status_code=500, detail=f"Preprocessor not found at {PREPROCESSOR_PATH}. Ensure it's trained and deployed.")
        if not os.path.exists(MODEL_PATH):
            logging.error(f"Model file not found at: {MODEL_PATH}")
            raise HTTPException(status_code=500, detail=f"Model not found at {MODEL_PATH}. Ensure it's trained and deployed.")

        preprocessor = load_object(PREPROCESSOR_PATH)
        model = load_object(MODEL_PATH)
        logging.info("Preprocessor and Model loaded successfully.")

        if TARGET_COLUMN in df.columns:
            logging.info(f"'{TARGET_COLUMN}' column found in input data, dropping it before prediction.")
            df_features = df.drop(columns=[TARGET_COLUMN], axis=1)
        else:
            df_features = df.copy() # Use a copy to avoid SettingWithCopyWarning if df is a slice


        network_model = NetworkModel(preprocessor, model)

        y_pred = network_model.predict(df_features) # Pass only features to the model for prediction
        df["predicted_column"] = y_pred
        logging.info("Predictions made successfully.")

        output_dir = "prediction_output"
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, "prediction.csv")
        df.to_csv(output_filepath, index=False)
        logging.info(f"Prediction output saved to: {output_filepath}")

        table_html = df.to_html(classes="table table-striped")

        # HTML template expects 'table' as the key, not 'table_html'
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})

    except HTTPException as http_exception:
        logging.error(f"HTTP Error in predict_route: {http_exception.detail}", exc_info=True)
        raise http_exception
    except Exception as e:
        logging.error(f"An unexpected error occurred in predict_route: {e}", exc_info=True)
        raise NetworkSecurityException(e, sys)
    
    
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)