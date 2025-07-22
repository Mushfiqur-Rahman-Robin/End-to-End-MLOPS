import os
import pandas as pd
from src.ds_end_to_end import logger
from sklearn.model_selection import train_test_split
from src.ds_end_to_end.entity.config_entity import DataTransformationConfig

class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    # note: you can add different data transformation techniques
    # i am only adding train test split
    # as the data is already cleaned up

    def train_test_spliting(self):
        data = pd.read_csv(self.config.data_path)

        train_data, test_data = train_test_split(data)

        train_data.to_csv(os.path.join(self.config.root_dir, "train.csv"), index = False)
        test_data.to_csv(os.path.join(self.config.root_dir, "test.csv"), index = False)

        logger.info("Splited data into train and test")
        logger.info(f"Train data: {train_data.shape}")
        logger.info(f"Test data: {test_data.shape}")