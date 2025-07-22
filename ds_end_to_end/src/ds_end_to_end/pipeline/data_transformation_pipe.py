from src.ds_end_to_end.components.data_transformation import DataTransformation
from src.ds_end_to_end import logger
from pathlib import Path
from src.ds_end_to_end.config.configuration import ConfigurationManager

STAGE_NAME = "Data Transformation stage"

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_transformation(self):
        try:
            with open(Path("artifacts/data_validation/status.txt"), "r") as f:
                status = f.read().split(" ")[-1]

            if status == "True":
                config = ConfigurationManager()
                data_transformation_config = config.get_data_transformation_config()
                data_transformation = DataTransformation(config=data_transformation_config)
                data_transformation.train_test_spliting()

            else:
                raise Exception("Data validation stage failed")

        except Exception as e:
            raise e

