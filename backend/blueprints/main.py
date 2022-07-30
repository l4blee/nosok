from sanic import Blueprint
from sanic.response import file


bp = Blueprint(
    'main'
)


@bp.route('/')
@bp.route('/<path:path>')
async def index(request, path: str = None):
    return await file('frontend/dist/index.html')
