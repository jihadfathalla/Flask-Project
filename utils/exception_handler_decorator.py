from flask import  jsonify
from .custom_exception_class import CustomException


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomException as e:
            return (
                jsonify(
                    {
                        "message": e.message,
                    },
                )),e.status_code,
            
    return wrapper