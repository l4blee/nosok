from abc import ABC, abstractmethod
from os import getenv

from discord import Colour

BASE_PREFIX = getenv('BASE_PREFIX', '!')
BASE_COLOR = Colour.from_rgb(241, 184, 19)
ERROR_COLOR = Colour.from_rgb(255, 0, 0)


class MusicHandlerBase(ABC):
    @abstractmethod
    async def get_url(self, query: str) -> str:
        """
        Returns a url for the first video found using query passed.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        """
        Returns a video url using query passed.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        """
        Gets query and returns information about the videos found.
        Output format should be a list of tuple(url, title, thumbnail)
        """
        # (url, title, thumbnail)
        raise NotImplementedError

    @abstractmethod
    async def get_info(self, query: str, is_url: bool = False) -> tuple[str, str]:
        """
        Gets query and returns information about the first video found.
        Output format should be tuple(url, title)
        """
        raise NotImplementedError

    @abstractmethod
    async def get_stream(self, url: str) -> str:
        """
        Requires a video url to be passed as an argument.
        Returns a url to a stream of the video passed.
        """
        raise NotImplementedError
