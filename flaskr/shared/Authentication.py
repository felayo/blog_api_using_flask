import os
from functools import wraps
from flask import request, jsonify, g
import jwt
from sqlalchemy.exc import NoResultFound

from ..models import UserModel


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token", None)
        secret = os.environ.get("JWT_SECRET_KEY")
        if token:
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                user_id = payload["id"]
                if user_id:
                    g.user = {'id': user_id}
                    return func(*args, **kwargs)

            except NoResultFound:
                return jsonify({"error": "No user found with provided token"}), 403
            except Exception as e:
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper
