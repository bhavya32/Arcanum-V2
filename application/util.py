from functools import wraps
from flask import jsonify, request
from flask import current_app
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_login import current_user

def librarian(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role=="student":
            return current_app.login_manager.unauthorized()

        return func(*args, **kwargs)

    return decorated_view


def admin(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims["role"] == "librarian":
            return fn(*args, **kwargs)
        else:
            return jsonify(msg="Admins only!"), 403

    return decorator
