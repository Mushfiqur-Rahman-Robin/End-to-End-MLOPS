import os
import sys
import mlflow.sklearn
import numpy as np
import pandas as pd
import mlflow

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact, ModelEvaluationArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier
)


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, x_train, y_train, x_test, y_test):
        logging.info("Starting model training within train_model method.")
        
        with mlflow.start_run() as run:
            run_id = run.info.run_id
            logging.info(f"MLflow Run ID: {run_id}")
            print(f"MLflow Run ID: {run_id}")

            models = {
                "Random Forest": RandomForestClassifier(verbose=0),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=0),
                "Logistic Regression": LogisticRegression(verbose=0, solver='liblinear'), 
                "AdaBoost": AdaBoostClassifier()
            }
            
            params = {
                "Decision Tree": {"criterion": ["gini", "entropy"]},
                "Random Forest": {
                    "criterion": ["gini", "entropy"],
                    "max_features": ["log2", "sqrt"],
                    "n_estimators": [50, 100, 150],
                },
                "AdaBoost": {
                    'learning_rate': [0.01, 0.1, 0.5, 1.],
                    'n_estimators': [50, 100, 150]
                },
                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05],
                    "subsample": [0.6, 0.7, 0.9],
                    "max_depth": [4, 5, 6],
                },
                "Logistic Regression": {
                    'penalty': ['l1', 'l2'],
                    'C': [0.001, 0.01, 0.1, 1, 10, 100]
                },
            }

            model_report: dict = evaluate_models(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test, models=models, params=params)
            
            filtered_model_report_values = [score for score in model_report.values() if not pd.isna(score)]
            
            if not filtered_model_report_values:
                raise Exception("All models failed to train or produce valid scores. Cannot determine best model.")

            best_model_score = max(filtered_model_report_values)

            best_model_name = None
            for name, score in model_report.items():
                if not pd.isna(score) and score == best_model_score:
                    best_model_name = name
                    break
            
            if best_model_name is None:
                raise Exception("Could not determine best model name even after filtering NaN scores.")

            best_model = models[best_model_name]
            
            logging.info(f"Retraining best model '{best_model_name}' on full training data.")
            mlflow.log_param("best_model_name", best_model_name)

            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
            logging.info(f"Train metrics for {best_model_name}: {classification_train_metric}")

            mlflow.log_metric("train_f1_score", classification_train_metric.f1_score)
            mlflow.log_metric("train_precision_score", classification_train_metric.precision_score)
            mlflow.log_metric("train_recall_score", classification_train_metric.recall_score)

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"Test metrics for {best_model_name}: {classification_test_metric}")

            mlflow.log_metric("test_f1_score", classification_test_metric.f1_score)
            mlflow.log_metric("test_precision_score", classification_test_metric.precision_score)
            mlflow.log_metric("test_recall_score", classification_test_metric.recall_score)

            diff = abs(classification_train_metric.f1_score - classification_test_metric.f1_score)
            if diff > self.model_trainer_config.overfitting_underfitting_threshold:
                logging.warning(f"Model is potentially overfitting or underfitting. Train F1: {classification_train_metric.f1_score}, Test F1: {classification_test_metric.f1_score}, Diff: {diff}")
                mlflow.log_param("overfitting_underfitting_status", "WARNING: Potential Overfitting/Underfitting")
            else:
                mlflow.log_param("overfitting_underfitting_status", "OK")

            if classification_test_metric.f1_score < self.model_trainer_config.expected_accuracy:
                logging.warning(f"Trained model does not meet expected accuracy. Expected: {self.model_trainer_config.expected_accuracy}, Actual: {classification_test_metric.f1_score}")
                mlflow.log_param("accuracy_threshold_status", "WARNING: Did Not Meet Expected Accuracy")
            else:
                mlflow.log_param("accuracy_threshold_status", "OK")

            logging.info("Loading preprocessor object.")
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            logging.info("Creating NetworkModel object (preprocessor + best model).")
            network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
            
            logging.info(f"Saving NetworkModel locally to {self.model_trainer_config.trained_model_file_path}")
            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=network_model)

            logging.info(f"Logging NetworkModel as MLflow artifact from {self.model_trainer_config.trained_model_file_path}")
            mlflow.log_artifact(local_path=self.model_trainer_config.trained_model_file_path, artifact_path="trained_model")

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(f"Model Trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact
        
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Initiating model training process.")
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            logging.info(f"Loading transformed train array from {train_file_path}")
            train_array = load_numpy_array_data(train_file_path)
            logging.info(f"Loading transformed test array from {test_file_path}")
            test_array = load_numpy_array_data(test_file_path)

            x_train, y_train = train_array[:, :-1], train_array[:, -1]
            x_test, y_test = test_array[:, :-1], test_array[:, -1]

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            
            logging.info("Model Trainer initiation completed.")
            return model_trainer_artifact
        
        except Exception as e:
            logging.error(f"Error in initiate_model_trainer: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)
