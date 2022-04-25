import json
from os import getenv
from pathlib import Path
from importlib import import_module

from flask import Flask, Response, jsonify

from handler import handler

if getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('bot/.env')

app = Flask(__name__)

if __name__ == '__main__':
    for i in Path('server/blueprints').glob('*.py'):
        mod = import_module(f'blueprints.{i.stem}')
        bp = mod.__dict__['bp']
        app.register_blueprint(bp)
    
    handler.launch()
    app.run('0.0.0.0', port=getenv('PORT', 8080))
