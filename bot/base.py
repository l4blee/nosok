from os import getenv
from abc import ABC

from discord import Colour

BASE_PREFIX = getenv('BASE_PREFIX', '!')
BASE_COLOR = Colour.from_rgb(241, 184, 19)
ERROR_COLOR = Colour.from_rgb(255, 0, 0)


class MusicHandlerBase(ABC):
    def get_url(self, query: str) -> str:
        raise NotImplementedError

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
