from src.ds_end_to_end.components.model_evaluation import ModelEvaluation
from src.ds_end_to_end import logger
from src.ds_end_to_end.config.configuration import ConfigurationManager
import mlflow

STAGE_NAME = "Model Evaluation stage"

class ModelEvaluationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_model_evaluation(self):
        try:
            mlflow.set_experiment(STAGE_NAME)
            logger.info(f"MLflow experiment set to: '{STAGE_NAME}'")

            config = ConfigurationManager()
            model_evaluation_config = config.get_model_evaluation_config()
            model_evaluation = ModelEvaluation(config=model_evaluation_config)
            model_evaluation.log_into_mlflow()
            logger.info("Model evaluation logging complete.")
        except Exception as e:
            logger.exception(f"Error during Model Evaluation stage: {e}")
            raise e

if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationTrainingPipeline()
        obj.initiate_model_evaluation()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e