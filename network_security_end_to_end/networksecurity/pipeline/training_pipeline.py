import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.cloud.s3_syncer import S3Sync

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig

from networksecurity.constants.training_pipeline import TRAINING_BUCKET_NAME


class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config: TrainingPipelineConfig = TrainingPipelineConfig()
        self.s3_sync = S3Sync()
        if not os.getenv("AWS_ACCESS_KEY_ID") or \
           not os.getenv("AWS_SECRET_ACCESS_KEY") or \
           not os.getenv("AWS_DEFAULT_REGION"):
            logging.warning("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) or AWS_DEFAULT_REGION environment variables are not fully set. S3 sync might fail.")


    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion process.")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Data Ingestion completed successfully.")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=data_validation_config)
            logging.info("Starting data validation process.")
            data_validation_artifact = data_validation.initiate_data_validation()
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) 
        
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=data_transformation_config)
            logging.info("Starting data transformation process.")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
            logging.info("Starting model trainer process.")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def sysc_artifact_dir_to_s3(self): # local to s3
        try:
            local_folder = self.training_pipeline_config.artifact_dir
            if not os.path.isdir(local_folder):
                logging.error(f"Local artifact directory not found: {local_folder}. Skipping S3 sync for artifacts.")
                return # Exit if directory does not exist

            timestamp_str = self.training_pipeline_config.timestamp.strftime("%m_%d_%Y_%H_%M_%S")
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{timestamp_str}"
            logging.info(f"Attempting to sync artifact directory '{local_folder}' to S3 bucket: '{aws_bucket_url}'")
            self.s3_sync.sync_folder_to_s3(folder=local_folder, aws_bucket_url=aws_bucket_url)
            logging.info("Artifact directory sync to S3 completed.")
        except Exception as e:
            logging.error(f"Error syncing artifact directory to S3: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)

    def sync_saved_model_dir_to_s3(self): # local model to s3
        try:
            local_folder = self.training_pipeline_config.model_dir # This is "final_models"
            if not os.path.isdir(local_folder):
                logging.error(f"Local model directory not found: {local_folder}. Skipping S3 sync for final models.")
                return # Exit if directory does not exist

            timestamp_str = self.training_pipeline_config.timestamp.strftime("%m_%d_%Y_%H_%M_%S")
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_models/{timestamp_str}"
            logging.info(f"Attempting to sync saved model directory '{local_folder}' to S3 bucket: '{aws_bucket_url}'")
            self.s3_sync.sync_folder_to_s3(folder=local_folder, aws_bucket_url=aws_bucket_url)
            logging.info("Saved model directory sync to S3 completed.")
        except Exception as e:
            logging.error(f"Error syncing saved model directory to S3: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)
            
        
    def run_pipeline(self):
        try:
            logging.info("Starting training pipeline.")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)

            logging.info("Syncing artifacts to S3...")
            self.sysc_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
            logging.info("S3 sync operations completed.")

            logging.info("Training pipeline completed successfully.")
            return model_trainer_artifact
        except Exception as e:
            logging.error(f"Training pipeline failed: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)