import os
import sys
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        try:
            command = f"aws s3 sync {folder} {aws_bucket_url}"
            logging.info(f"Executing S3 sync command: {command}")
            print(f"Executing S3 sync command: {command}")
            
            # Execute the command and capture its exit status
            exit_code = os.system(command)
            
            if exit_code != 0:
                # AWS CLI returns non-zero exit code on failure
                logging.error(f"S3 sync command failed with exit code {exit_code} for folder: {folder}")
                raise Exception(f"AWS S3 sync command failed for folder '{folder}'. Check AWS CLI output for details.")
            
            logging.info(f"S3 sync command executed successfully for folder: {folder}")
        except Exception as e:
            logging.error(f"Error during S3 sync to S3 for folder {folder}: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)
    
    def sync_folder_from_s3(self, folder, aws_bucket_url):
        try:
            command = f"aws s3 sync {aws_bucket_url} {folder}"
            logging.info(f"Executing S3 sync command: {command}")
            print(f"Executing S3 sync command: {command}")
            
            exit_code = os.system(command)

            if exit_code != 0:
                logging.error(f"S3 sync command failed with exit code {exit_code} from S3 bucket: {aws_bucket_url}")
                raise Exception(f"AWS S3 sync command failed from S3 bucket '{aws_bucket_url}'. Check AWS CLI output for details.")

            logging.info(f"S3 sync command executed successfully from S3 bucket: {aws_bucket_url}")
        except Exception as e:
            logging.error(f"Error during S3 sync from S3 for bucket {aws_bucket_url}: {e}", exc_info=True)
            raise NetworkSecurityException(e, sys)