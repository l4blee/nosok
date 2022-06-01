import flask_socketio
import logging


socket = flask_socketio.SocketIO(manage_session=False)
logger = logging.getLogger('polling')


@socket.on('connect')
def connect():
    logger.info('connected')


@socket.on('disconnect')
def disconnect():
    logger.info('disconnected')

