from sanic import Blueprint
from sanic.response import file


bp = Blueprint(
    'main'
)


@bp.route('/')
async def index(request):
    return await file('web_platform/nosok-solid/dist/index.html')
