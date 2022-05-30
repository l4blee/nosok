import json
from flask import (Blueprint, Response,
                   jsonify, send_from_directory, request,
                   redirect)


bp = Blueprint(
    'main',
    __name__
)

import logging
logger = logging.getLogger('rdfsdf')

@bp.route('/')
@bp.route('/index')
def index():
    if request.path == '/index':
        return redirect('/')

    return send_from_directory('nosok-react/build', 'index.html')
