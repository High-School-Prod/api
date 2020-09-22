import secrets, hashlib
from sanic import Blueprint
from sanic.response import json, redirect
from src import sessions
from src.user.models import User
from src.user.utils import authorized, current_user

user = Blueprint("user_bp", url_prefix="/user")


@user.get('/auth')
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
			response.cookies['session']['secure'] = True
			response.cookies['session']['httponly'] = True
			response.cookies['session']['max-age'] = 60 * 60 * 24 * 30
			sessions[hs] = user.id
		else:
			response = json({'error': "No user"})
	else:
		response = json({'error': "No args"})

	return response


@user.route("/logout")
@authorized()
async def logout(request):
	response = redirect("/")
	del sessions[request.cookies.get('session')]
	del response.cookies['session']
	return response

@user.route("/")
@authorized()
async def main(request):
	response = json({"user": (await current_user(request)).username})
	return response