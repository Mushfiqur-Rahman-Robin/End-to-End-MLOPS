import os
import sys
import pandas as pd
import numpy as np
import pickle
import warnings
import logging
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet

import mlflow

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Set MLflow tracking URI from .env
REMOTE_SERVER_URI = os.getenv("REMOTE_SERVER_URI")
mlflow.set_tracking_uri(REMOTE_SERVER_URI)

# Evaluation function
def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # Load dataset
    csv_url = "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    try:
        data = pd.read_csv(csv_url, sep=";")
    except Exception as e:
        logger.exception(
            "Unable to download training & test CSV, check your internet connection. Error: %s", e
        )
        sys.exit(1)

    # Train-test split
    train, test = train_test_split(data)
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # Hyperparameters from CLI or defaults
    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    # Start MLflow run
    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        rmse, mae, r2 = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet model (alpha={alpha:.6f}, l1_ratio={l1_ratio:.6f}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        # Log parameters and metrics
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # Save model locally
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, "elasticnet_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(lr, f)
        print(f"✅ Model saved locally at {model_path}")

        # Log model as artifact (instead of using model registry)
        mlflow.log_artifact(model_path, artifact_path="model")
        print("📦 Model logged as MLflow artifact under 'model/'")