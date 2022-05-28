from os import getenv
import json

from flask import Blueprint, Response, render_template
from flask_login import login_required

from handlers import bot_handler

bp = Blueprint(
    'control',
    __name__,
    url_prefix='/control'
)


def jsonify(**kwargs):
    response = Response(json.dumps(kwargs, indent=4))
    response.mimetype = 'application/json'
    response.content_type = 'application/json'
    return response


@bp.route('/')
def index():
    return render_template('control.html')


@bp.route('/launch')
@login_required
def launch():
    resp = jsonify(**bot_handler.launch())
    return resp


@bp.route('/terminate')
@login_required
def terminate():
    resp = jsonify(**bot_handler.terminate())
    return resp


@bp.route('/restart')
@login_required
def restart():
    resp = jsonify(**bot_handler.restart())
    return resp


@bp.route('/log')
@login_required
def log():
    with open('bot/data/log.log') as f:
        data = f.read()
        
    resp = Response(data)
    resp.headers['Content-type'] = 'application/json'
    
    return resp


@bp.route('/vars')
@login_required
def vars():
    with open('bot/data/data.json') as f:
        data = json.load(f)
    
    return jsonify(**data)