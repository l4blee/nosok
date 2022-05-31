import json
from io import FileIO
import os
import logging
from subprocess import Popen, TimeoutExpired
from sys import executable

from pymongo import MongoClient

SUBPROCESS_CMD = [executable, 'bot/index.py']


class BotHandler:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__qualname__)
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
        self._logger.info('Launching bot...')
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
        self._logger.info('Terminating bot...')
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
        self._logger.info('Restarting bot...')
        self.terminate()
        self.set_status('restarting')
        self.launch()

        return dict(status='success', message=None)


class MongoDB:
    def __init__(self, conn_url):
        self._logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)
        self.connect(conn_url)
    
    def connect(self, conn_url: str):
        self._logger.info('Connecting to MongoDB...')

        self.client = MongoClient(conn_url)
        self.users = self.client.web.users  # Main database
        
        self._logger.info('Successfully connected to Mongo, going further...')


database = MongoDB(os.getenv('DATABASE_URL') % {
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
})
bot_handler = BotHandler()
