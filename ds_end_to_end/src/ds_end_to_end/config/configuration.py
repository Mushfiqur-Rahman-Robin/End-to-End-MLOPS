import sys
from src.ds_end_to_end.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from src.ds_end_to_end.utils.common import read_yaml, create_directories
from pathlib import Path
from src.ds_end_to_end.entity.config_entity import (DataIngestionConfig, DataValidationConfig)

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