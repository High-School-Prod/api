import secrets
import hashlib
from sanic import Blueprint
from sanic.response import json, redirect
from src import sessions
from src.user.models import User
from src.user.utils import authorized, current_user


user = Blueprint("user_bp", url_prefix="/user")


@user.route('/login', methods=['POST', 'OPTIONS'])
async def auth(request):
    if request.cookies.get('session') in sessions:
        return redirect('/')

	if request.args.get("username") and request.args.get("password"):
		username = request.args.get("username")
		password = hashlib.sha3_512(bytes(request.args.get("password"), encoding='utf8')).hexdigest()
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
			sessions[hs] = user
		else:
			response = json({'error': "No user"})
	else:
		response = json({'error': "No args"})

	if request.method == 'OPTIONS':
		response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
		response.headers['Access-Control-Allow-Methods'] = 'POST'
		response.headers['Access-Control-Allow-Credentials'] = 'true'
	if request.method == 'POST':
		response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
		response.headers['Access-Control-Allow-Credentials'] = 'true'

	return response


@user.get("/logout")
@authorized()
async def logout(request):
	response = redirect("/")
	del sessions[request.cookies.get('session')]
	del response.cookies['session']
	return response

@user.get("/<user_id:int>")
@user.get("/")
@authorized()
async def main(request, user_id=None):
    if user_id:
        user = await User.query.where(
            (User.id == user_id)
        ).gino.first()
    else:
        user = await current_user(request)
    if user:
        response = json({
            'id': user.id,
            'username': user.username,
            'status': user.status,
            'nickname': user.nickname,
            'avatar':  user.avatar,
            'email':  user.email
        })
    else:
        response = json({"error": "No user"}, 404)
    return response
