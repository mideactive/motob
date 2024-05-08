import logging

def init_error_log():
    logging.basicConfig(filename='error.log', level=logging.ERROR)

def log_error(exception):
    logging.error(str(exception))
