import os
import sys

from dataclasses import dataclass

from src.exception import CustomException
from src.logger import logging

from catboost import CatBoostRegressor
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV

from src.utils import save_object, evaluate_models


@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')


class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.model = None

    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info('Splitting training and test input data')

            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "K-Neighbors Regressor": KNeighborsRegressor(),
                "XGBRegressor": XGBRegressor(),
                "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor()
            }

            params = {
                "Decision Tree": {
                    'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    'splitter': ['best', 'random'],
                    'max_features': [None, 'sqrt', 'log2'],
                },  
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                    'max_features': ['sqrt', 'log2', None],
                    'max_depth': [2, 4, 6, 8, 10],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'bootstrap': [True, False],
                },
                "Gradient Boosting": {
                    'learning_rate': [0.1, 0.01, 0.05],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                    'max_depth': [2, 4, 6, 8, 10],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None],
                },
                "Linear Regression": {},
                "K-Neighbors Regressor": {
                    'n_neighbors': [4, 6, 8, 10, 12],
                    'weights': ['uniform', 'distance'],
                    'p': [1, 2]
                },
                "XGBRegressor": {
                    'learning_rate': [0.1, 0.01, 0.05],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                    'max_depth': [2, 4, 6, 8, 10],
                    'min_child_weight': [1, 2, 3],
                    'gamma': [0, 0.1, 0.2],
                    'subsample': [0.6, 0.7, 0.8, 0.9],
                    'colsample_bytree': [0.6, 0.7, 0.8, 0.9],
                    'reg_alpha': [0, 0.1, 0.2],
                    'reg_lambda': [0, 0.1, 0.2]
                },
                "CatBoosting Regressor": {
                    'depth': [6, 8, 10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },
                "AdaBoost Regressor": {
                    'n_estimators': [50, 100, 150],
                    'learning_rate': [0.1, 0.5, 1.0]
                }
            }

            model_report:dict = evaluate_models(X_train, y_train, X_test, y_test, models, params)
            print(model_report)
            best_model_score = max(sorted(model_report.values()))

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model_type = models[best_model_name]
            best_params = params[best_model_name]
            
            final_gs = GridSearchCV(best_model_type, best_params, cv=3, n_jobs=-1, verbose=2)
            final_gs.fit(X_train, y_train)
            best_model = final_gs.best_estimator_
            
            if best_model_score < 0.6:
                raise CustomException("No best model found with R2 score >= 0.6")
            
            logging.info(f"Best found model on both training and testing dataset: {best_model_name}")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predicted = best_model.predict(X_test)

            r2_square = r2_score(y_test, predicted)
            return r2_square

        except Exception as e:
            raise CustomException(e, sys)