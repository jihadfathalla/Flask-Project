import logging


def setup_logger(logger_name, log_file):
    # Configure the logging format
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    logger = logging.getLogger(logger_name)

    file_handler = logging.FileHandler(log_file)

    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger