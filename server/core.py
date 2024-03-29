import os
import logging
from pathlib import Path
from importlib import import_module
from dataclasses import dataclass

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

import bson
import bcrypt

from api import api_manager
from polling import socket
from handlers import database, bot_handler

logger = logging.getLogger('core')


@dataclass(slots=True)
class User:
    """
    Represents a user document in MongoDB.
    Required to be used with flask_login.
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


def load_blueprints(path: os.PathLike) -> None:
    logger.info(f'Loading blueprints from {path}')
    for i in Path(path).glob('*.py'):
        mod = import_module(f'blueprints.{i.stem}')
        bp = mod.__dict__['bp']
        app.register_blueprint(bp)

    logger.info(f'Available blueprints: {list(app.blueprints.keys())}')


app = Flask(
    __name__,
    static_folder='nosok-react/build/static'
)
app.config['SECRET_KEY'] = '02f24e90200099ec055f17819b97910a67571a11d762df36'
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 2  # equal to 2 hours

if os.getenv('APP_STATUS', 'production') != 'production':
    app.config['TEMPLATES_AUTO_RELOAD'] = True

load_blueprints('server/blueprints')

cors = CORS(app)
login_manager = LoginManager(app)
api_manager.init_app(app)
socket.init_app(app)


@login_manager.user_loader
def load_user(email):
    record = database.users.find_one({
        'email': email
    })

    return User.from_record(record)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

bot_handler.launch()
logger.info('Initialized `core` module')
