from dataclasses import dataclass

import bson
import bcrypt
from flask_login import LoginManager

from handlers import database

login_manager = LoginManager()


@dataclass()
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


@login_manager.user_loader
def load_user(email):
    record = database.users.find_one({
        'email': email
    })

    return User.from_record(record)
