import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import as_declarative
import discord

load_dotenv('.env')
engine = create_engine(os.environ.get('POSTGRES_URL'))
BASE_PREFIX = os.environ.get('BASE_PREFIX')
BASE_COLOR = discord.Colour.from_rgb(241, 184, 19)
ERROR_COLOR = discord.Colour.from_rgb(255, 0, 0)

REACTIONS_OPTS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


@as_declarative(
    metadata=MetaData(bind=engine)
)
class Base:
    __tablename__ = ...
