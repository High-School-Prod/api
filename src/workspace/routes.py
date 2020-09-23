from sanic import Blueprint, response


workspace = Blueprint("workspace_bp", url_prefix="/workspace")


@workspace.get("/")
async def main(request):
    return response.json({'hello': 'world'})
