from dataclasses import dataclass
from functools import wraps
from typing import Optional
import bson

import bcrypt
import jwt
from sanic import Sanic
from sanic.response import text


@dataclass
class User:
    """
    Represents a user document in MongoDB.
    """
    email: str
    password: bson.Binary
    salt: bson.Binary
    is_admin: bool = False

    @classmethod
    def from_record(cls, record: dict):
        if record is None:
            return None

        return cls(
            email=record.get('email'),
            password=record.get('password'),
            salt=record.get('salt'),
            is_admin=record.get('is_admin', False)
        )

    def to_dict(self) -> dict:
        return {
            'email': self.email,
            'password': self.password.decode('utf-8'),
            'salt': self.salt.decode('utf-8'),
            'is_admin': self.is_admin
        }

    def check_password(self, password: bytes) -> bool:
        hashed_pwd = bcrypt.hashpw(password, self.salt)
        return hashed_pwd == self.password


class LoginManager:
    def __init__(self, app=None):
        self.app = app
        self._storage = dict()
        self.COOKIE_MAX_AGE = 2 * 60 * 60  # 2 hours in seconds

    def init_app(self, app: Sanic) -> None:
        async def extract_user(request):
            '''
            Middleware to be called before request
            '''
            user = None

            token = request.cookies.get('session', None)
            if token is not None:
                user = manager.get_user(token)

            request.ctx.user = user if type(user) is User else None

        app.register_middleware(extract_user, 'request')
        self.app = app
        self._COOKIE_MAX_AGE = app.config.REMEMBER_COOKIE_DURATION
        self._SECRET = app.config.SECRET

    def login_user(self, user: User) -> str:
        token = jwt.encode({
                'user': user.to_dict()
            },
            self._SECRET,
            'HS256'
        )

        return token
    
    def get_user(self, token: str) -> Optional[User]:
        try:
            serialized = jwt.decode(
                token,
                self._SECRET,
                algorithms=['HS256']
            ).get('user')

            user = User(
                email=serialized.get('email'),
                password=serialized.get('password').encode('utf-8'),
                salt=serialized.get('salt').encode('utf-8'),
                is_admin=serialized.get('is_admin')
            )
        except Exception:
            return None
        
        return user



def login_required(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request.ctx.user:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function
    return decorator(wrapped)


manager = LoginManager()
