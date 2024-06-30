from logs.logger_utils import setup_logger
from utils.custom_exception_class import CustomException
from datetime import datetime

read_methods = set("GET")


def view_logging_aspect(logger_name, log_file_path):
    logger = setup_logger(logger_name, log_file_path)

    def decorator(view_method):
        def wrapper(*args, **kwargs):
            request = args[1]
            user = request.user
            try:
                response = view_method(*args, **kwargs)

                logger.info(
                    f"user {user.id if not user.is_anonymous else user} called successfully {request} with data {request.data} at {datetime.now()}"
                ) if request.method not in read_methods else ...
            except CustomException as e:
                logger.error(
                    f"user {user.id if not user.is_anonymous else user} called wrongfully {request} with data {request.data} with errors {e.errors or e.message} at {datetime.now()}"
                )

                raise e
            except Exception as e:
                logger.exception(
                    f"user {user.id if not user.is_anonymous else user} called wrongfully {request} with data {request.data} with Exception {e} at {datetime.now()}"
                )

                raise e

            return response

        return wrapper

    return decorator