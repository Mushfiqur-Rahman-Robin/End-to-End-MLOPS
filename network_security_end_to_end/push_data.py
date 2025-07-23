import os
import sys
import json
import certifi
import pandas as pd
import pymongo
import numpy as np
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD")

uri = f"mongodb+srv://{username}:{password}@cluster0.ywc3jur.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

ca = certifi.where()

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json_converter(self, file__path):
        try:
            data = pd.read_csv(file__path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records
            self.mongo_client = pymongo.MongoClient(uri, tlsCAFile=ca)

            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return (len(self.records))

        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    FILE_PATH = "network_data/phisingData.csv"
    DATABASE = "network_security"
    COLLECTION = "phising_data"
    networkobj = NetworkDataExtract()
    records = NetworkDataExtract().csv_to_json_converter(file__path=FILE_PATH)
    no_of_records = NetworkDataExtract().insert_data_mongodb(records=records, database=DATABASE, collection=COLLECTION)
    logging.info(f"Number of records inserted in mongodb: {no_of_records}")
    print(f"Number of records inserted in mongodb: {no_of_records}")
    