import os
import json
from threading import Lock
import logging

import flask_socketio

logger = logging.getLogger('polling')

socket = flask_socketio.SocketIO(manage_session=True, cors_allowed_origins='*')
connected_clients: int = 0

thread_lock = Lock()
thread = None

def bg_thread():
    global connected_clients

    cached_stamp_log = 0
    cached_stamp_vars = 0

    while 1:
        try:
            log_stamp = os.stat('bot/data/log.log').st_mtime
            vars_stamp = os.stat('bot/data/data.json').st_mtime

            if log_stamp != cached_stamp_log:
                with open('bot/data/log.log') as f:
                    socket.emit('data_changed', {
                        'href': '/log',
                        'content': f.read()
                    })
                cached_stamp_log = log_stamp

            if vars_stamp != cached_stamp_vars:
                with open('bot/data/data.json') as f:
                    socket.emit('data_changed', {
                        'href': '/vars',
                        'content': json.load(f)
                    })
                cached_stamp_vars = vars_stamp
        except:
            pass


@socket.on('connect')
def connect():
    global thread, connected_clients
    with thread_lock:
        if thread is None:
            thread = socket.start_background_task(bg_thread)

    connected_clients += 1


@socket.on('disconnect')
def disconnect():
    global connected_clients
    connected_clients -= 1
