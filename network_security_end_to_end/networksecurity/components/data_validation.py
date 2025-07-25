from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

from scipy.stats import ks_2samp
import os
import sys
import pandas as pd

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    @staticmethod
    def read_data(fule_path) -> pd.DataFrame:
        try:
            return pd.read_csv(fule_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_config["COLUMNS"]) 
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Actual number of columns: {len(dataframe.columns)}")

            if len(dataframe.columns) == number_of_columns:
                return True
            
            error_message = f"Data validation failed. Required number of columns: {len(self._schema_config['COLUMNS'])} and Actual number of columns: {len(dataframe.columns)}"
            logging.error(error_message)
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if is_same_dist.pvalue > threshold:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column: 
                               {
                                   "p_value": float(is_same_dist.pvalue),
                                   "drift_status": is_found
                               }    
                               })
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            # create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            write_yaml_file(drift_report_file_path, report)
            
            return status

        except Exception as e:    
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            logging.info("Validating number of columns in train data.")
            is_train_cols_valid = self.validate_number_of_columns(train_dataframe)
            if not is_train_cols_valid:
                raise Exception("Train data column validation failed.")

            logging.info("Validating number of columns in test data.")
            is_test_cols_valid = self.validate_number_of_columns(test_dataframe)
            if not is_test_cols_valid:
                raise Exception("Test data column validation failed.")


            numerical_columns_from_schema = self._schema_config.get("numerical_columns", [])
            if not all(col in train_dataframe.columns for col in numerical_columns_from_schema):
                error_message = f"Data validation failed. Numerical columns: {numerical_columns_from_schema} are not present in the train dataset."
                logging.error(error_message)
                raise Exception(error_message)

            if not all(col in test_dataframe.columns for col in numerical_columns_from_schema):
                error_message = f"Data validation failed. Numerical columns: {numerical_columns_from_schema} are not present in the test dataset."
                logging.error(error_message)
                raise Exception(error_message)
            
            logging.info("Numerical columns validated successfully.")

            # check data drift
            logging.info("Detecting data drift between train and test datasets.")
            drift_status = self.detect_dataset_drift(train_dataframe, test_dataframe)

            # Ensure valid/invalid directories are created for output
            valid_dir_path = self.data_validation_config.valid_data_dir
            invalid_dir_path = self.data_validation_config.invalid_data_dir
            os.makedirs(valid_dir_path, exist_ok=True)
            os.makedirs(invalid_dir_path, exist_ok=True)


            if drift_status:
                logging.info("No data drift detected. Saving validated data.")
                valid_train_path = self.data_validation_config.valid_train_file_path
                valid_test_path = self.data_validation_config.valid_test_file_path
                invalid_train_path = None
                invalid_test_path = None
                
                train_dataframe.to_csv(valid_train_path, index=False, header=True)
                test_dataframe.to_csv(valid_test_path, index=False, header=True)

            else:
                logging.warning("Data drift detected. Saving invalid data.")
                valid_train_path = None
                valid_test_path = None
                invalid_train_path = self.data_validation_config.invalid_train_file_path
                invalid_test_path = self.data_validation_config.invalid_test_file_path

                train_dataframe.to_csv(invalid_train_path, index=False, header=True)
                test_dataframe.to_csv(invalid_test_path, index=False, header=True)

            data_validation_artifact = DataValidationArtifact(
                validation_status=drift_status,
                validation_train_file_path=valid_train_path,
                validation_test_file_path=valid_test_path,
                invalid_train_file_path=invalid_train_path,
                invalid_test_file_path=invalid_test_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            logging.info(f"Data Validation Artifact: {data_validation_artifact}")
            return data_validation_artifact
            
        except Exception as e:
            logging.error(f"Error in initiate_data_validation: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)