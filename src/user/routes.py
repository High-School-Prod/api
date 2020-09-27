import secrets, datetime

from sanic import Blueprint
from sanic.response import json, redirect
from sanic.views import HTTPMethodView

from src import sessions, db
from src.user.models import User
from src.user.utils import authorized, has_json_body, current_user, encode_to_sha


user = Blueprint("user_bp", url_prefix="/user")


@user.route('/login', methods=['POST', 'OPTIONS'])
@has_json_body()
async def login(request):
    """Authorizes user"""
    session = request.cookies.get('session')
    if session and sessions.get("session:" + session):
        return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Already authorized'
                    }
        }, 423)

    if ((username := request.json.get("username"))
            and (password := request.json.get("password"))):

        user = await User.query.where(
            (User.username == username)
            & (User.password == encode_to_sha(password))).gino.first()

        if user:
            hs = secrets.token_hex(nbytes=16)
            response = json({
                    'ok': True,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Authorized'
                    }
            })
            response.cookies['session'] = hs
            response.cookies['session']['httponly'] = True
            response.cookies['session']['max-age'] = 60 * 60 * 24 * 30
            sessions.set("session:" + hs, user.id)
            return response
        else:
            return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Authorization failed'
                    }
            }, 400)
    else:
        return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Missing parameters'
                    }
        }, 406)


@user.route('/logout', methods=['POST', 'OPTIONS'])
@authorized()
async def logout(request):
    """Deauthorizes user"""
    response = json({
                    'ok': True,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Deauthorized'
                    }
    }, 200)
    sessions.delete("session:" + request.cookies.get('session'))
    del response.cookies['session']
    return response


@user.route("/", methods=['POST', 'OPTIONS'])
@authorized()
async def get_user(request):
    """Gets user by id"""
    user_id = request.json.get("id")
    if not user_id:
        user = await current_user(request)
    else:
        if type(user_id) != int:
            return json({
                'ok': False,
                'data': {},
                'status': {
                    'datetime': str(datetime.datetime.now()),
                    'message': 'Expected integer'
                }
            }, 400)
        user = await User.query.where(
                (User.id == int(user_id))).gino.first()

    if user:
        return json({
                    'ok': True,
                    'data': {
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'status': user.status,
                            'nickname': user.nickname,
                            'avatar':  user.avatar,
                            'email':  user.email
                        }
                    },
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                    }
        }, 200)
    else:
        return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'User not found'
                    }
        }, 404)


@user.route("/add-user", methods=['POST', 'OPTIONS'])
@has_json_body()
async def add_user(request):
    """Adds user"""
    username = request.json.get("username")
    password = request.json.get("password")
    nickname = request.json.get("nickname")
    email = request.json.get("email")

    if username and password and email:
        user = User(
            username=username,
            password=encode_to_sha(password),
            nickname=nickname if nickname else username,
            email=email
        )
        if await user.validate():
            await user.create()
            return json({
                    'ok': True,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': f"User added with id {user.id}"
                    }
            }, 200)

        return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'User is already in base'
                    }
        }, 409)

    return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Missing parameters'
                    }
        }, 400)


@user.route("/del-user", methods=['POST', 'OPTIONS'])
@has_json_body()
async def del_user(request):
    """Removes user"""
    if user_id := request.json.get("id"):
        if type(user_id) != int:
            return json({
                        'ok': False,
                        'data': {},
                        'status': {
                            'datetime': str(datetime.datetime.now()),
                            'message': 'Expected integer'
                        }
            }, 400)
        user = await User.query.where(
            User.id == request.json.get("id")
        ).gino.first()

        if user:
            await user.delete()
            return json({
                    'ok': True,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'User deleted'
                    }
        }, 200)

        return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'User is not in database'
                    }
        }, 404)

    return json({
                    'ok': False,
                    'data': {},
                    'status': {
                        'datetime': str(datetime.datetime.now()),
                        'message': 'Missing parameters'
                    }
        }, 400)