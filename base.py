import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import as_declarative

load_dotenv('.env')
engine = create_engine(os.environ.get('DATABASE_URL'))
BASE_PREFIX = os.environ.get('BASE_PREFIX')


@as_declarative(
    metadata=MetaData(bind=engine)
)
class Base:
    __tablename__ = ...
