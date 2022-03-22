from os import getenv

from flask import Blueprint, Response, jsonify, request

from handler import handler

bp = Blueprint(
    'control',
    __name__
)

def check_auth(params):
    password, username = params.get('password'), params.get('username')
    return username == getenv('app_username') and password == getenv('app_password')


@bp.route('/launch')
def launch():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(message='Unathorized'), 401
        
    resp = Response(f'Status: {handler.launch()}')
    resp.headers['Content-type'] = 'application/json'
    return resp


@bp.route('/terminate')
def terminate():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(message='Unathorized'), 401

    resp = Response(f'Status: {handler.terminate()}')
    resp.headers['Content-type'] = 'application/json'
    return resp


@bp.route('/restart')
def restart():
    params = request.args.to_dict()
    if not check_auth(params):
        return jsonify(message='Unathorized'), 401

    resp = Response(f'Status: {handler.restart()}')
    resp.headers['Content-type'] = 'application/json'
    return resp


