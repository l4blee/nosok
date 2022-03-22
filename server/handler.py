import json
from io import FileIO
from os import makedirs
from logging import getLogger
from subprocess import Popen, TimeoutExpired
from sys import executable

SUBPROCESS_CMD = [executable, 'bot/index.py']


class BotHandler:
    def __init__(self):
        self._logger = getLogger(self.__class__.__qualname__)
        self.check_dirs()

        self.bot_proc = None
        self.pout = FileIO('bot/data/log.log', mode='a+')

    def check_dirs(self):
        makedirs('bot/data/', exist_ok=True)

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

    def launch(self) -> str:
        self._logger.info('Launching bot...')
        if self.bot_proc is not None:
            return 'The bot is already online!'
        
        self.bot_proc = Popen(
            SUBPROCESS_CMD,
            stdout=self.pout,
            stderr=self.pout
        )
        self.set_status('online')
        return 'Success'

    def terminate(self) -> str:
        self._logger.info('Terminating bot...')
        if self.bot_proc is None:
            return 'The bot is already offline!'

        try:
            self.bot_proc.terminate()
            self.bot_proc.wait(timeout=5)
        except TimeoutExpired:
            self.bot_proc.kill()
        finally:
            self.bot_proc = None
        
        self.set_status('offline')
        return 'Success'

    def restart(self) -> str:
        self._logger.info('Restarting bot...')
        self.terminate()
        self.launch()

        return 'Success'


handler = BotHandler()
