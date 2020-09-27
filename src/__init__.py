from pymemcache.client.base import Client
from sanic import Sanic
from src.config import Config
from gino.ext.sanic import Gino

sessions = Client(('127.0.0.1', 11211))
sessions.flush_all()

app = Sanic(__name__)
app.config.from_object(Config)
db = Gino()
db.init_app(app)

from src.workspace import workspace
from src.user import user

app.blueprint(workspace)
app.blueprint(user)


@app.middleware('response')
async def middleware_handler(request, response):
    """Sets headers for CORS"""
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    if request.method == 'POST':
        response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
        response.headers['Access-Control-Allow-Credentials'] = 'true'


@app.listener('after_server_stop')
async def close_redis(app, loop):
    sessions.close()