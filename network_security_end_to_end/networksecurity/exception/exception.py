import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_detail:sys):
        self.error_message = error_message
        _, _, exc_tb = error_detail.exc_info()

        self.line_number = exc_tb.tb_frame.f_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return "Error occured in script: [{0}] at line number: [{1}] error message: [{2}]".format(
            self.file_name, self.line_number, self.error_message
        )
    
# if __name__ == "__main__":
#     try:
#         logger.logging.info("Entering the try block")
#         a = 1/0
#         print("This will not execute")
#     except Exception as e:
#         logger.logging.info("Divide by zero")
#         raise NetworkSecurityException(e, sys)