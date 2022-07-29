import json
from io import FileIO
import os
from subprocess import Popen, TimeoutExpired
from sys import executable

SUBPROCESS_CMD = [executable, 'bot/index.py']


class BotHandler:
    def __init__(self):
        self.check_dirs()

        self.bot_proc = None
        self.pout = FileIO('bot/data/log.log', mode='a+')

    def check_dirs(self):
        os.makedirs('bot/data/', exist_ok=True)

        with open('bot/data/data.json', 'w') as f:
            f.write('{"status": "offline"}')

        with open('bot/data/log.log', 'w') as f:
            f.write('')

    def set_status(self, status: str) -> None:
        with open('bot/data/data.json') as f:
            data = json.load(f)

        with open('bot/data/data.json', 'w') as f:
            data['status'] = status
            json.dump(data, f, indent=4)

    def launch(self) -> dict:
        if self.bot_proc is not None:
            return dict(status='error', message='The bot is already online!')

        self.bot_proc = Popen(
            SUBPROCESS_CMD,
            stdout=self.pout,
            stderr=self.pout
        )
        self.set_status('online')
        return dict(status='success', message=None)

    def terminate(self) -> dict:
        if self.bot_proc is None:
            return dict(status='error', message='The bot is already offline!')

        try:
            self.bot_proc.terminate()
            self.bot_proc.wait(timeout=5)
        except TimeoutExpired:
            self.bot_proc.kill()
        finally:
            self.bot_proc = None

        self.set_status('offline')
        return dict(status='success', message=None)

    def restart(self) -> dict:
        self.terminate()
        self.set_status('restarting')
        self.launch()

        return dict(status='success', message=None)


bot_handler = BotHandler()
