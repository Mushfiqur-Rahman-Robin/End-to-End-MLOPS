import os
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import mlflow
import mlflow.sklearn
import joblib
from pathlib import Path
from urllib.parse import urlparse
from src.ds_end_to_end import logger
from src.ds_end_to_end.utils.common import save_json
from src.ds_end_to_end.entity.config_entity import ModelEvaluationConfig

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    def log_into_mlflow(self):
        test_data = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path) # Load the trained model

        test_x = test_data.drop([self.config.target_column], axis=1)
        test_y = test_data[[self.config.target_column]]

        mlflow.set_registry_uri(self.config.mlflow_uri)
        # No need to check tracking_url_type_store if we are always using log_artifact
        # tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run():
            predicted_qualities = model.predict(test_x)

            (rmse, mae, r2) = self.eval_metrics(test_y, predicted_qualities)

            # Saving metrics as local JSON file
            scores = {"rmse": rmse, "mae": mae, "r2": r2}
            save_json(path=self.config.metric_file_name, content=scores)
            logger.info(f"Metrics saved to: {self.config.metric_file_name}")

            # Log parameters and metrics to MLflow
            mlflow.log_params(self.config.all_params)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("mae", mae)

            mlflow.log_artifact(local_path=str(self.config.model_path), artifact_path="model")
            logger.info(f"Model logged as artifact '{self.config.model_path.name}' to MLflow run.")

        logger.info("Metrics and model logged to MLflow successfully!")