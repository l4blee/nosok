from asyncio import CancelledError, sleep
import os
import json

from socketio import AsyncServer


socket = AsyncServer(async_mode='sanic', cors_allowed_origins='*')


async def background_emitter():
    cached_stamp_log = 0
    cached_stamp_vars = 0

    while 1:
        try:
            log_stamp = os.stat('bot/data/log.log').st_mtime
            vars_stamp = os.stat('bot/data/data.json').st_mtime

            if log_stamp != cached_stamp_log:
                with open('bot/data/log.log') as f:
                    await socket.emit('data_changed', {
                        'changed': 'log',
                        'content': f.read()
                    })
                cached_stamp_log = log_stamp

            if vars_stamp != cached_stamp_vars:
                with open('bot/data/data.json') as f:
                    await socket.emit('data_changed', {
                        'changed': 'variables',
                        'content': json.load(f)
                    })
                cached_stamp_vars = vars_stamp

            await sleep(0.2)
        except CancelledError:
            return
        except Exception:
            pass
