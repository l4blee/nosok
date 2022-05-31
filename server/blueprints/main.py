import json
import os
from flask import Blueprint, send_from_directory


bp = Blueprint(
    'main',
    __name__
)

import logging
logger = logging.getLogger('rdfsdf')

@bp.route('/')
def index():
    return send_from_directory('nosok-react/build', 'index.html')
