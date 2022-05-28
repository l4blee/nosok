import json

from flask import (Blueprint, Response,
                   jsonify, render_template, request,
                   redirect)


bp = Blueprint(
    'main',
    __name__
)


@bp.route('/')
@bp.route('/index')
def index():
    if request.path == '/index':
        return redirect('/')
    return render_template('index.html')

