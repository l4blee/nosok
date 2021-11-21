import abc
import os

import discord
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

load_dotenv('bot/.env')
engine = create_engine(os.environ.get('POSTGRES_URL'))
Session = sessionmaker(bind=engine)


BASE_PREFIX = os.environ.get('BASE_PREFIX')
BASE_COLOR = discord.Colour.from_rgb(241, 184, 19)
ERROR_COLOR = discord.Colour.from_rgb(255, 0, 0)


@as_declarative(
    metadata=MetaData(bind=engine)
)
class DBBase:
    __tablename__ = ...


class MusicHandlerBase(abc.ABC):
    def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        raise NotImplementedError

    def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        # (url, title, thumbnail)
        raise NotImplementedError

    def get_info(self, query: str, is_url: bool = False) -> tuple[str, str]:
        # (url, title) is enough
        raise NotImplementedError

    def get_stream(self, url: str) -> str:
        raise NotImplementedError
