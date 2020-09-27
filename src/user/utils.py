import hashlib, datetime
from functools import wraps
from src import sessions, db
from sanic.response import json
from src.user.models import User

def authorized():
    """Decorator to check if connection is authorized"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = sessions.get("session:" + request.headers.get('Authorization')) # checking if we have a token key in session dict
            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Not an authorized request'
                    }}, 401)
        return decorated_function
    return decorator

def has_json_body():
    """Decorator to check if request have json body"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request.json:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'No request body'
                    }}, 400)
        return decorated_function
    return decorator

def options_responser():
    """Checks if OPTIONS method"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request.method == 'OPTIONS':
                return json({'options': 'ok'})
            response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator



async def current_user(request):
    """Return current session user object if exists else None"""
    user = await User.query.where(
        User.id == int(sessions.get('session:'+request.headers.get('Authorization')))
    ).gino.first()
    return user

def encode_to_sha(s):
    return hashlib.sha3_512(bytes(s, encoding='utf8')).hexdigest()