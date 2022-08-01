from dataclasses import dataclass
import bcrypt
import bson
from sanic import Blueprint
from sanic.response import redirect, text, json

from auth import manager, User, login_required
from database import database


bp = Blueprint(
    'login',
    url_prefix='/auth'
)

@dataclass
class LoginRegisterPayload:
    email: str
    password: str

    @classmethod
    def from_request(cls, request):
        data = request.json

        email = data.get('email')
        password = data.get('password')

        return cls(email, password)


@bp.route('/signin', methods=['POST'])
async def login(request):
    payload = LoginRegisterPayload.from_request(request)
    record = database.users.find_one({
        'email': payload.email
    })

    if record is not None:
        user = User.from_record(record)
        if user.check_password(payload.password.encode('utf-8')):
            # Server-to-client side auth
            token = manager.login_user(user)  
            resp = redirect('/')
            resp.cookies['session'] = token
            resp.cookies['session']['max-age'] = manager.COOKIE_MAX_AGE

            return resp

    return json({
        'message': 'unauth'
    })

@bp.route('/signup', methods=['POST'])
async def register(request):
    payload = LoginRegisterPayload.from_request(request)
    record = database.users.find_one({
        'email': payload.email
    })

    if record is not None:
        return json({
            'message': 'already exists'
        })

    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(payload.password, salt)
    user = User(
        email=payload.email,
        password=bson.Binary(hashed_pwd),
        salt=bson.Binary(salt)
    )

    # Server-to-client side auth
    database.users.insert_one(user.to_dict())
    uuid = manager.login_user(user)  
    resp = redirect('/')
    resp.cookies['session'] = uuid
    resp.cookies['session']['max-age'] = manager.COOKIE_MAX_AGE

    return resp


@bp.route('/logout')
async def logout(request):
    resp = redirect('/')
    if 'session' in request.cookies:
        del resp.cookies['session']

    return resp


@bp.route('/secret')
@login_required
async def secret(request):
    return text('welcome!')
