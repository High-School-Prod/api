from functools import wraps
from src import sessions
from sanic.response import json
from src.user.models import User


def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = request.cookies.get('session') in sessions
            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({'status': 'not_authorized'}, 403)
        return decorated_function
    return decorator


async def current_user(request):
    user = sessions[request.cookies.get('session')]
    return user
