from dataclasses import dataclass
from functools import wraps
import bson
import uuid

import bcrypt
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

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self) -> str:
        return self.email

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
        return {i: getattr(self, i) for i in self.__slots__}

    def check_password(self, password: bytes) -> bool:
        hashed_pwd = bcrypt.hashpw(password, self.salt)
        return hashed_pwd == self.password


class LoginManager:
    def __init__(self, app=None):
        self.app = app
        self._storage = dict()
        self.COOKIE_MAX_AGE = 2 * 60 * 60  # 2 hours in seconds

    def init_app(self, app: Sanic) -> None:
        async def request(request):
            '''
            Middleware to be called before request
            '''
            if request.cookies.get('session', None) is not None:
                user = manager.get_user(request)
                
                request.ctx.is_authenticated = user is not None
                request.ctx.user = user
            else:
                request.ctx.is_authenticated = False
                request.ctx.user = None

        app.middleware(request)
        self.app = app

    def login_user(self, user: User) -> str:
        if user in self._storage.values():
            return [i for i, j in self._storage.items() if j is user][0]

        unique_uid = uuid.uuid1().hex
        self._storage[unique_uid] = user

        return unique_uid
    
    def get_user(self, request):
        uid = request.cookies.get('session', None)
        if uid is None:
            return None

        return self._storage.get(uid)


def login_required(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request.ctx.is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function
    return decorator(wrapped)


manager = LoginManager()
