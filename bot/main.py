import os
import logging
from urllib.parse import urlparse
from json import load, dump, dumps
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import FileIO
from subprocess import Popen, TimeoutExpired
from sys import executable

if os.getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('bot/.env')

SUBPROCESS_CMD = [executable, f'{os.getcwd()}/bot/index.py']


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if os.path.exists(f'{os.getcwd()}/bot/data/data.json'):
            with open(f'{os.getcwd()}/bot/data/data.json') as f:
                data = load(f)
        else:
            data = {
                'status': 'offline',
                'vars': {
                    'servers': int('Nan'),
                    'latency': float('Nan'),
                    'memory_used': float('Nan')
                },
                'last_updated': datetime.now().strftime('%d.%b.%Y %H:%M:%S')
            }
        parsed = urlparse(self.path)

        if parsed.path in ['/launch', '/terminate', '/restart']:
            if parsed.query:
                try:
                    query = dict(map(lambda x: tuple(x.split('=')), parsed.query.split('&')))
                except ValueError:
                    query = dict()
            else:
                query = dict()

            if query.get('password') != os.getenv('app_password') or\
                query.get('username') != os.getenv('app_username'):
                self.send_error(401)
                return

            bot = self.server.bot_process

        if parsed.path == '/launch':
            self.server._logger.info('Launching bot...')
            if bot is not None:
                out = 'Status: the bot is already online!'
            else:
                self.server.bot_process = Popen(
                    SUBPROCESS_CMD,
                    stdout=self.server.pout,
                    stderr=self.server.pout
                )
                out = 'Status: done'
        elif parsed.path == '/terminate':
            if bot is None:
                out = 'Status: the bot is already offline'
            else:
                self.server._logger.info('Terminating bot...')
                self.terminate_bot()
                out = 'Status: done'
        elif parsed.path == '/restart':
            self.server._logger.info('Restarting bot...')

            if bot is not None:
                self.terminate_bot()

            self.server.bot_process = Popen(
                SUBPROCESS_CMD,
                stdout=self.server.pout,
                stderr=self.server.pout
            )
            out = 'Status: done'
        elif parsed.path == '/':
            out = f'Status: {data["status"]}'
        elif parsed.path == '/vars':
            out = dumps(data, indent=4)
        elif parsed.path == '/log':
            with open(f'{os.getcwd()}/bot/data/log.log') as f:
                out = f.read()
        elif parsed.path == '/favicon.ico':
            self.send_response(200, 'OK')
            return
        else:
            self.send_error(409)
            return

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(out.encode('utf-8'))

    def do_POST(self):
        username, password = self.headers.get('Authorization').split(':')

        if not (username == os.environ.get('app_username')
                and password == os.environ.get('app_password')):
            self.send_error(401)
            return

        bot: Popen = self.server.bot_process
        parsed = urlparse(self.path)

        if parsed.path == '/launch':
            self.server._logger.info('Launching bot...')
            if bot is not None:
                self.send_error(409)
                return
            else:
                self.server.bot_process = Popen(
                    SUBPROCESS_CMD,
                    stdout=self.server.pout,
                    stderr=self.server.pout
                )
        elif parsed.path == '/terminate':
            self.server._logger.info('Terminating bot...')
            self.terminate_bot()
        elif parsed.path == '/restart':
            self.server._logger.info('Restarting bot...')
            self.terminate_bot()

            self.server.bot_process = Popen(
                SUBPROCESS_CMD,
                stdout=self.server.pout,
                stderr=self.server.pout
            )
        else:
            self.send_error(400)
            return

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write('Status: done'.encode('utf-8'))

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
            data = load(f)

        with open(f'{os.getcwd()}/bot/data/data.json', 'w') as f:
            data['status'] = 'offline'

            dump(data, f, indent=4)


class Server(HTTPServer):
    __slots__ = ('_logger', 'bot_process')

    def __init__(self):
        super().__init__(
            ('0.0.0.0', int(os.environ.get('PORT', 5000))),
            RequestHandler
        )
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self.bot_process = None
        self.check_dirs()

    def check_dirs(self):
        os.makedirs(f'{os.getcwd()}/bot/data/', exist_ok=True)

        with open(f'{os.getcwd()}/bot/data/data.json', 'w'):
            ...

        with open(f'{os.getcwd()}/bot/data/log.log', 'w'):
            ...

    def run_server(self):
        self._logger.info('Starting bot itself...')
        self.pout = FileIO(f'{os.getcwd()}/bot/data/log.log', mode='a+')

        self.bot_process = Popen(
            SUBPROCESS_CMD,
            stdout=self.pout,
            stderr=self.pout
        )

        self._logger.info('Starting Server...')
        self.serve_forever()

    def close(self):
        self._logger.info('Closing Server...')
        self.server_close()


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

http_server = Server()

try:
    http_server.run_server()
except:
    pass
finally:
    http_server.close()
