import os
from abc import ABC

import discord
from dotenv import load_dotenv

load_dotenv('bot/.env')

BASE_PREFIX = os.environ.get('BASE_PREFIX')
BASE_COLOR = discord.Colour.from_rgb(241, 184, 19)
ERROR_COLOR = discord.Colour.from_rgb(255, 0, 0)


class MusicHandlerBase(ABC):
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
