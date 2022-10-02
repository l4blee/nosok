from sanic import Sanic
from sanic.log import logger

from polling import socket, background_emitter
from handlers import bot_handler
from utils import load_blueprints
from auth import manager

app = Sanic(__name__)
app.static('/assets', 'frontend/dist/assets')

app.config.SECRET = '02f24e90200099ec055f17819b97910a67571a11d762df36'
app.config.REMEMBER_COOKIE_DURATION = 60 * 60 * 2  # equal to 2 hours

socket.attach(app)
manager.init_app(app)

load_blueprints(app, 'backend/blueprints')


@app.listener('before_server_start')
async def before_server_start(app: Sanic, loop):
    socket.start_background_task(background_emitter)
    bot_handler.launch()
    logger.info('Started background Socket.IO task and Bot handler, proceeding further...')


@app.listener('before_server_stop')
async def before_server_stop(app: Sanic, loop):
    bot_handler.terminate()
