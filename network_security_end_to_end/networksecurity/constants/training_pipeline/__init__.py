import os
import sys
import numpy as np
import pandas as pd

# defining common constants for training pipeline

TARGET_COLUMN: str = "Result"
ARTIFACT_DIR: str = "artifacts"
PIPELINE_NAME: str = "network_security"
FILE_NAME: str = "phishingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

# data ingestion related constants

DATA_INGESTION_COLLECTION_NAME: str = "phishing_data"
DATA_INGESTION_DATABASE_NAME: str = "network_security"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2