from json import load

from sanic import Blueprint
from sanic.response import json


bp = Blueprint(
    'api',
    url_prefix='/api'
)


@bp.route('/vars')
async def vars(request):
    with open('bot/data/data.json') as f:
        data = load(f)

    return json({
        'message': 'OK',
        'content': data
    })


@bp.route('/log')
async def log(request):
    with open('bot/data/log.log') as f:
        data = f.read()

    return json({
        'message': 'OK',
        'content': data
    })
