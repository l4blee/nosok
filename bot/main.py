import logging
import requests
import subprocess
import json
import os
from http import server
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv('bot/.env')
PYTHON_PATH = os.environ.get('_')


class RequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        bot: subprocess.Popen = self.server.bot_process
        if bot is None:
            self.send_error(409, message='Bot is offline')
            return

        res = requests.get('http://localhost:5001' + self.path)
        data = res.json()

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode('utf-8')
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        username, password = self.headers.get('Authorization').split(':')

        if not (username == os.environ.get('app_username')
                and password == os.environ.get('app_password')):
            self.send_error(401)
            return

        bot: subprocess.Popen = self.server.bot_process

        if parsed.path == '/terminate':
            print('terminating')
            try:
                bot.wait(timeout=5)
            except subprocess.TimeoutExpired:
                bot.kill()
            finally:
                self.server.bot_process = None
        elif parsed.path == '/launch':
            print('launching bot')
            if bot is not None:
                self.send_error(409)
                return
            else:
                self.server.bot_process = subprocess.Popen(f'{PYTHON_PATH} ./bot/index.py')
        elif parsed.path == '/restart':
            print('restarting')
            try:
                bot.wait(timeout=5)
            except subprocess.TimeoutExpired:
                bot.kill()

            self.server.bot_process = subprocess.Popen(f'{PYTHON_PATH} ./bot/index.py')
        else:
            self.send_error(400)
            return

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(
            'Done'.encode('utf-8')
        )


class Server(server.HTTPServer):
    def __init__(self):
        super().__init__(
            ('0.0.0.0', int(os.environ.get('PORT', 5000))),
            RequestHandler
        )
        self._logger = logging.getLogger('index')
        self.bot_process = None

    def run_server(self):
        self._logger.info('Starting bot itself')
        self.bot_process = subprocess.Popen(f'{PYTHON_PATH} ./bot/index.py')

        self._logger.info('Starting Server')
        self.serve_forever()

        self.close()

    def close(self):
        self._logger.info('Closing Server')
        self.server_close()
        self._logger.info('Server closed successfully')


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')

http_server = Server()
print(os.environ)
http_server.run_server()
