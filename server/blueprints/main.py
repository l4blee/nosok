import logging

from flask import Blueprint, send_from_directory, send_file


bp = Blueprint(
    'main',
    __name__
)

logger = logging.getLogger('rdfsdf')


@bp.route('/')
def index():
    return send_from_directory('nosok-react/build', 'index.html')


@bp.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico')
