from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import os
import sys
import numpy as np
import pymongo
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

from dotenv import load_dotenv
load_dotenv()


username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD")

uri = f"mongodb+srv://{username}:{password}@cluster0.ywc3jur.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            
            logging.info(f"Attempting to connect to MongoDB and retrieve data from database: '{database_name}', collection: '{collection_name}'")
            print(f"Attempting to connect to MongoDB and retrieve data from database: '{database_name}', collection: '{collection_name}'")
            self.mongo_client = pymongo.MongoClient(uri)
            collection = self.mongo_client[database_name][collection_name]

            documents = list(collection.find())
            df = pd.DataFrame(documents)

            logging.info(f"DataFrame initial size after fetching from MongoDB: {len(df)} rows")
            print(f"DataFrame initial size after fetching from MongoDB: {len(df)} rows")

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

                logging.info(f"DataFrame size after dropping '_id' column: {len(df)} rows")
                print(f"DataFrame size after dropping '_id' column: {len(df)} rows")

            df.replace("", np.nan, inplace=True) 
            logging.info(f"DataFrame size after replacing empty strings with NaN: {len(df)} rows")
            print(f"DataFrame size after replacing empty strings with NaN: {len(df)} rows")

            df.dropna(inplace=True) 
            logging.info(f"DataFrame size after dropping rows with NaN values: {len(df)} rows")
            print(f"DataFrame size after dropping rows with NaN values: {len(df)} rows")

            if df.empty:
                logging.warning("DataFrame is EMPTY after all processing in export_collection_as_dataframe. This will cause issues for train_test_split.")
                print("DataFrame is EMPTY after all processing in export_collection_as_dataframe. This will cause issues for train_test_split.")
            return df
        
        except Exception as e:
            logging.error(f"Error during data extraction from MongoDB: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)
        
    def export_data_to_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            if dataframe.empty:
                logging.error("Cannot perform train-test split: Input DataFrame is empty.")
                raise ValueError("Cannot perform train-test split: Input DataFrame is empty.")

            train_set, test_set = train_test_split(dataframe, test_size = self.data_ingestion_config.train_test_split_ratio)
            logging.info("Performed train test split on the dataframe")

            dir_path = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info("Exporting train data to feature store")

            train_set.to_csv(self.data_ingestion_config.train_file_path, index=False, header=True)

            logging.info("Exporting test data to feature store")
            test_set.to_csv(self.data_ingestion_config.test_file_path, index=False, header=True)

        except Exception as e:    
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            logging.info("Starting data ingestion process.")
            dataframe = self.export_collection_as_dataframe()
            
            if dataframe.empty:
                logging.error("Dataframe is empty after exporting from collection. Aborting further steps.")
                print("Dataframe is empty after exporting from collection. Aborting further steps.")
            else:
                logging.info(f"Successfully retrieved {len(dataframe)} rows from MongoDB.")
                print(f"Successfully retrieved {len(dataframe)} rows from MongoDB.")

            dataframe = self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.train_file_path,
                test_file_path=self.data_ingestion_config.test_file_path,
            )
            logging.info("Data Ingestion completed successfully.")
            return dataingestionartifact

        except Exception as e:
            logging.error(f"Error in initiate_data_ingestion: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)