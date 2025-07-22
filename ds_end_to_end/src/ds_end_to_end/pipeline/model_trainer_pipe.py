from src.ds_end_to_end.components.model_trainer import ModelTrainer
from src.ds_end_to_end import logger
from src.ds_end_to_end.config.configuration import ConfigurationManager

STAGE_NAME = "Model Trainer stage"

class ModelTrainerTrainingPipeline:
    def __init__(self):
        self.config = ConfigurationManager()
        self.model_trainer = ModelTrainer(config=self.config.get_model_trainer_config())

    def initiate_model_training(self):
        config = ConfigurationManager()
        model_trainer_config = config.get_model_trainer_config()
        model_trainer = ModelTrainer(config=model_trainer_config)
        model_trainer.train()