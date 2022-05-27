from os import getenv
from json import dumps

from flask import Blueprint, Response, request

from handlers import bot_handler

bp = Blueprint(
    'control',
    __name__
)

def jsonify(**kwargs):
    response = Response(dumps(kwargs, indent=4))
    response.mimetype = 'application/json'
    response.content_type = 'application/json'
    return response

def check_auth(params):
    password, username = params.get('password'), params.get('username')
    return username == getenv('app_username') and password == getenv('app_password')


@bp.route('/launch')
def launch():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(status='error', message='Unathorized'), 401
        
    resp = jsonify(**bot_handler.launch())
    resp.headers['Content-type'] = 'application/json'
    return resp


@bp.route('/terminate')
def terminate():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(message='Unathorized'), 401

    resp = jsonify(**bot_handler.terminate())
    resp.headers['Content-type'] = 'application/json'
    return resp


@bp.route('/restart')
def restart():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(message='Unathorized'), 401

    resp = jsonify(**bot_handler.restart())
    resp.headers['Content-type'] = 'application/json'
    return resp


