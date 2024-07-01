from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or role not in [r.name for r in current_user.roles]:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
