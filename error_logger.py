import logging
import traceback
import sys

def init_error_log():
    logging.basicConfig(filename='error.log', level=logging.ERROR)

def log_error(exception):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    logging.error(f"Exception occurred in file {filename}, line {line_number}: {str(exception)}")
