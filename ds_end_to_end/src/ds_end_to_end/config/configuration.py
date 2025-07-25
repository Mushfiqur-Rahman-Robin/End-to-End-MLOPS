import os
import sys
from src.ds_end_to_end.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from src.ds_end_to_end.utils.common import read_yaml, create_directories
from pathlib import Path
from src.ds_end_to_end.entity.config_entity import (DataIngestionConfig, 
    DataValidationConfig, 
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig
)

class ConfigurationManager:
    def __init__(
        self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH,
        schema_filepath: Path = SCHEMA_FILE_PATH
    ):
        self.base_path = Path(sys.path[0])

        absolute_config_path = self.base_path / config_filepath
        absolute_params_path = self.base_path / params_filepath
        absolute_schema_path = self.base_path / schema_filepath

        self.config = read_yaml(absolute_config_path)
        self.params = read_yaml(absolute_params_path)
        self.schema = read_yaml(absolute_schema_path)

        create_directories([self.base_path / Path(self.config.artifacts_root)])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        ingestion_root_dir = self.base_path / Path(config.root_dir)
        ingestion_local_data_file = self.base_path / Path(config.local_data_file)
        ingestion_unzip_dir = self.base_path / Path(config.unzip_dir)

        create_directories([ingestion_root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=ingestion_root_dir,
            source_URL=config.source_URL,
            local_data_file=ingestion_local_data_file,
            unzip_dir=ingestion_unzip_dir
        )

        return data_ingestion_config
    
    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        schema = self.schema.COLUMNS

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            STATUS_FILE=config.STATUS_FILE,
            unzip_data_dir = config.unzip_data_dir,
            all_schema=schema
        )

        return data_validation_config
    
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation

        create_directories([config.root_dir])

        data_transformation_config = DataTransformationConfig(
            root_dir=config.root_dir,
            data_path=config.data_path,
        )

        return data_transformation_config
    
    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        params = self.params.ElasticNet
        schema = self.schema.TARGET_COLUMN

        create_directories([config.root_dir])

        model_trainer_config = ModelTrainerConfig(
            root_dir=config.root_dir,
            train_data_path=config.train_data_path,
            test_data_path=config.test_data_path,
            model_name=config.model_name,
            alpha=params.alpha,
            l1_ratio=params.l1_ratio,
            target_column=schema.name
        )

        return model_trainer_config
    
    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation

        params = self.params.ElasticNet
        schema = self.schema.TARGET_COLUMN

        create_directories([config.root_dir])

        model_evaluation_config = ModelEvaluationConfig(
            root_dir=Path(config.root_dir),
            test_data_path=Path(config.test_data_path), #config.test_data_path,
            model_path=Path(config.model_path), #config.model_path,
            all_params=params,
            metric_file_name=Path(config.metric_file_name), #config.metric_file_name,
            target_column=schema.name,
            mlflow_uri=os.getenv("MLFLOW_TRACKING_URI"),
        )

        return model_evaluation_config