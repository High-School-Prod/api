from sanic import Sanic
from src.config import Config
from gino.ext.sanic import Gino

sessions = {}

app = Sanic(__name__)
app.config.from_object(Config)
db = Gino()
db.init_app(app)

from src.workspace import workspace
from src.user import user

app.blueprint(workspace) 
app.blueprint(user) 
