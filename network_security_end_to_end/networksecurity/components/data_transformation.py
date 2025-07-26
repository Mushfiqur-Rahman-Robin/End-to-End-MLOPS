import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constants.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod # Changed from 'cls' to 'self' or just make it static without 'cls'
    def get_Data_transformer_object() -> Pipeline:
        logging.info("Entered the get_Data_transformer_object method of DataTransformation class")
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            processor = Pipeline(steps=[("imputer", imputer)])
            logging.info("Exited the get_Data_transformer_object method of DataTransformation class")
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Starting data transformation process.")
        try:
            logging.info("Reading train and test file.")
            # Ensure to read from validation artifact's validated paths
            train_df = DataTransformation.read_data(self.data_validation_artifact.validation_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.validation_test_file_path)

            # training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0) # Adjust target values if -1 should be 0

            # testing dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0) # Adjust target values if -1 should be 0

            preprocessor = DataTransformation.get_Data_transformer_object() # Call static method correctly
            
            # Fit the preprocessor on the training features
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            
            # Transform both train and test features
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            # Concatenate transformed features with target
            train_arr =  np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Save transformed train and test numpy arrays
            logging.info(f"Saving transformed train numpy array to {self.data_transformation_config.transformed_train_file_path}")
            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=train_arr # Corrected 'arrary' to 'array' if your utils.py expects 'array'
            )
            logging.info(f"Saving transformed test numpy array to {self.data_transformation_config.transformed_test_file_path}")
            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_test_file_path,
                array=test_arr # Corrected 'arrary' to 'array' if your utils.py expects 'array'
            )

            # Save the fitted preprocessor object
            logging.info(f"Saving preprocessor object to {self.data_transformation_config.transform_object_file_path}")
            save_object(
                file_path=self.data_transformation_config.transform_object_file_path,
                obj=preprocessor_object
            )

            save_object("final_models/preprocessor.pkl", preprocessor_object)
            
            # Create and return DataTransformationArtifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transform_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            logging.info(f"Data Transformation completed. Artifact: {data_transformation_artifact}")
            return data_transformation_artifact

        except Exception as e:
            logging.error(f"Error in initiate_data_transformation: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)