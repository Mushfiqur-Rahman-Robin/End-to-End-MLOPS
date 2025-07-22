import urllib.request as request
import zipfile
from src.ds_end_to_end import logger
from src.ds_end_to_end.entity.config_entity import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        if not self.config.local_data_file.exists():
            filename, headers = request.urlretrieve(
                url = self.config.source_URL,
                filename = str(self.config.local_data_file)
            )
            logger.info(f"{filename} download! with following info: \n{headers}")
        else:
            logger.info(f"File '{self.config.local_data_file}' already exists!")

    def extract_zip_file(self):
        """
        Extracts the zip file into the data directory
        """
        unzip_path = self.config.unzip_dir
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)
        logger.info(f"Zip file extracted to: {unzip_path}")