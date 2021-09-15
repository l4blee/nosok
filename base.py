import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import as_declarative
from dotenv import load_dotenv


load_dotenv()
engine = create_engine(os.environ.get('POSTGRES_URL'))
metadata = MetaData(bind=engine)


@as_declarative(metadata=metadata)
class Base:
    pass
