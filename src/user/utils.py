from functools import wraps
import hashlib
from src import sessions, db
from sanic.response import json
from src.user.models import User

def authorized():
    """Decorator to check if connection is authorized"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = sessions.get("session:" + request.cookies.get('session')) # checking if we have a token key in session dict
            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({'error': 'Not authorized request'}, 403)
        return decorated_function
    return decorator


async def current_user(request):
    """Return current session user object if exists else None"""
    user = await User.query.where(
        User.id == int(sessions.get('session:'+request.cookies.get('session')))
    ).gino.first()
    return user

def encode_to_sha(s):
    return hashlib.sha3_512(bytes(s, encoding='utf8')).hexdigest()