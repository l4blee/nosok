from sanic import Sanic
from sanic.log import logger

from polling import socket, background_emitter
from handlers import bot_handler
from utils import load_blueprints

app = Sanic(__name__)
app.static('/assets', 'web_platform/nosok-solid/dist/assets')

load_blueprints(app, 'web_platform/blueprints')

socket.attach(app)


@app.listener('before_server_start')
async def before_server_start(sanic, loop):
    socket.start_background_task(background_emitter)
    bot_handler.launch()
    logger.info('Started background Socket.IO task and Bot handler, proceeding further...')


@app.listener('before_server_stop')
async def before_server_stop(sanic, loop):
    bot_handler.terminate()
