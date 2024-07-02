from functools import wraps
from flask_jwt_extended import  current_user
from flask import  jsonify 


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or role !=current_user.role.name :
                return jsonify({"error": "you don't have permission for this request"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
