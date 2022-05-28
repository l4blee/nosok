import json
import os
import logging
from pathlib import Path
from importlib import import_module
from dataclasses import dataclass

from flask import Flask, Response, jsonify
from flask_login import LoginManager

import bson
import bcrypt

from handlers import database

logger = logging.getLogger('core')


@dataclass(slots=True)
class User:
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
    for i in Path(path).glob('*.py'):
        mod = import_module(f'blueprints.{i.stem}')
        bp = mod.__dict__['bp']
        app.register_blueprint(bp)
    
    logger.info(f'Available blueprints: {list(app.blueprints.keys())}')


app = Flask(__name__)
app.config['SECRET_KEY'] = '12312312312312312'
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 2  # equal to 2 hours

if os.getenv('APP_STATUS', 'production') != 'production':
    app.config['TEMPLATES_AUTO_RELOAD'] = True

load_blueprints('server/blueprints')

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(email):
    record = database.users.find_one({
        'email': email
    })
    
    return User.from_record(record)
