import json
import logging
import os
from http import server
from io import FileIO
from subprocess import Popen, TimeoutExpired
from sys import executable
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv('bot/.env')
SUBPROCESS_CMD = [executable, f'{os.getcwd()}/bot/index.py']


class RequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if os.path.exists('bot/data/data.json'):
            with open(f'{os.getcwd()}/bot/data/data.json') as f:
                data = json.load(f)
        else:
            data = {
                'status': 'offline',
                'vars': {
                    'servers': [],
                    'latency': float('Nan'),
                    'memory_used': float('Nan')
                }
            }

        if self.path == '/':
            out = {
                'status': data['status']
            }
        elif self.path == '/vars':
            out = data['vars']
        elif self.path == '/log':
            with open(f'{os.getcwd()}/bot/data/log.log') as f:
                out = {
                    'content': f.read()
                }
        else:
            self.send_error(409)
            return

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(
            json.dumps(out).encode('utf-8')
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        username, password = self.headers.get('Authorization').split(':')

        if not (username == os.environ.get('app_username')
                and password == os.environ.get('app_password')):
            self.send_error(401)
            return

        bot: Popen = self.server.bot_process

        if parsed.path == '/launch':
            print('launching bot')
            if bot is not None:
                self.send_error(409)
                return
            else:
                self.server.bot_process = Popen(
                    SUBPROCESS_CMD,
                    stdout=self.server.pout[0],
                    stderr=self.server.pout[1]
                )
        elif parsed.path == '/terminate':
            print('terminating')
            self.terminate_bot()
        elif parsed.path == '/restart':
            print('restarting')
            self.terminate_bot()

            self.server.bot_process = Popen(
                SUBPROCESS_CMD,
                stdout=self.server.pout[0],
                stderr=self.server.pout[1]
            )
        else:
            self.send_error(400)
            return

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(
            'Done'.encode('utf-8')
        )

    def terminate_bot(self):
        bot: Popen = self.server.bot_process

        try:
            bot.terminate()
            bot.wait(timeout=5)
        except TimeoutExpired:
            bot.kill()
        finally:
            self.server.bot_process = None

        with open(f'{os.getcwd()}/bot/data/data.json') as f:
            data = json.load(f)

        with open(f'{os.getcwd()}/bot/data/data.json', 'w') as f:
            data['status'] = 'offline'

            json.dump(data, f, indent=4)


class Server(server.HTTPServer):
    def __init__(self):
        super().__init__(
            ('0.0.0.0', int(os.environ.get('PORT', 5000))),
            RequestHandler
        )
        self._logger = logging.getLogger('index')
        self.bot_process = None
        self.check_dirs()

    def check_dirs(self):
        if not os.path.exists('bot/data'):
            os.makedirs('bot/data')

        with open('bot/data/data.json', 'w'):
            pass

        with open('bot/data/log.log', 'w'):
            pass

    def run_server(self):
        self._logger.info('Starting bot itself...')
        self.pout = FileIO('bot/data/log.log', mode='a')

        self.bot_process = Popen(
            SUBPROCESS_CMD,
            stdout=self.pout,
            stderr=self.pout
        )

        self._logger.info('Starting Server...')
        self.serve_forever()

        self.close()

    def close(self):
        self._logger.info('Closing Server...')
        self.server_close()


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')

http_server = Server()
http_server.run_server()
