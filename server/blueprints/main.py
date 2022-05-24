import json

from flask import Blueprint, Response, jsonify


bp = Blueprint(
    'main',
    __name__
)


@bp.route('/')
def index():
    with open('bot/data/data.json') as f:
        data = json.load(f)
        
    resp = jsonify(status=data['status'])
    resp.headers['Content-type'] = 'application/json'
    
    return resp
    

@bp.route('/log')
def log():
    with open('bot/data/log.log') as f:
        data = f.read()
        
    resp = Response(data)
    resp.headers['Content-type'] = 'application/json'
    resp.headers['Connection'] = 'keep-alive'
    
    return resp


@bp.route('/vars')
def vars():
    with open('bot/data/data.json') as f:
        data = json.load(f)

    resp = jsonify(**data)
    resp.headers['Content-type'] = 'application/json'
    
    return resp
