import secrets

from sanic import Blueprint
from sanic.response import json, redirect
from sanic.views import HTTPMethodView

from src import sessions, db
from src.user.models import User
from src.user.utils import authorized, current_user, encode_to_sha


user = Blueprint("user_bp", url_prefix="/user")


@user.route('/login', methods=['POST', 'OPTIONS'])
async def login(request):
    """Authorizes user"""

    session = request.cookies.get('session')
    if session and sessions.get("session:" + session):
        return json({'error': "Already authorized"})

    if request.args.get("username") and request.args.get("password"):
        username = request.args.get("username")
        password = encode_to_sha(request.args.get("password"))
        user = await User.query.where(
            (User.username == username)
            & (User.password == password)
        ).gino.first()

        if user:
            hs = secrets.token_hex(nbytes=16)
            response = json({'token': user.username})
            response.cookies['session'] = hs
            response.cookies['session']['httponly'] = True
            response.cookies['session']['max-age'] = 60 * 60 * 24 * 30
            sessions.set("session:" + hs, user.id)
            return response
        else:
            return json({'error': "Authorization failed"})
    else:
        return json({'error': "Expected arguments {username, password}"})


@user.route('/logout', methods=['GET', 'OPTIONS'])
@authorized()
async def logout(request):
    """Deauthorizes user"""
    response = json({"success": "Deauthorized"})
    sessions.delete("session:" + request.cookies.get('session'))
    del response.cookies['session']
    return response


@user.route("/get_user", methods=['GET', 'OPTIONS'])
@authorized()
async def get_user(request):
    """Gets user by id"""
    user_id = request.args.get("id")
    if not user_id:
        user = await current_user(request)
    else:
        if not user_id.isnumeric():
            return json({"error": "Needs integer"})
        else:
            user = await User.query.where(
                (User.id == int(user_id))
            ).gino.first()

    if user:
        return json({
            'id': user.id,
            'username': user.username,
            'status': user.status,
            'nickname': user.nickname,
            'avatar':  user.avatar,
            'email':  user.email
        })
    else:
        return json({"error": "No user"}, 404)


@user.route("/add_user", methods=['POST', 'OPTIONS'])
async def add_user(request):
    """Adds user"""
    username = request.args.get("username")
    password = request.args.get("password")
    nickname = request.args.get("nickname")
    email = request.args.get("email")

    if username and password and email:
        user = User(
            username=username,
            password=encode_to_sha(password),
            nickname=nickname if nickname else username,
            email=email
        )
        if await user.validate():
            await user.create()
            return json({"success": "User added"}, 200)

        return json({"error": "User already in base"})

    return json({"error": "Missing parameters"})


@user.route("/del_user", methods=['POST', 'OPTIONS'])
async def del_user(request):
    """Removes user"""
    if request.args.get("id"):
        user = await User.query.where(
                User.id == int(request.args.get("id"))
        ).gino.first()

        if user:
            await user.delete()
            return json({"success": "Deleted user"})

        return json({"error": "User not in base"})

    return json({"error": "Missing parameters"})