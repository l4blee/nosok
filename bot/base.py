from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from os import getenv

from discord import Colour
from discord.ext import commands

BASE_PREFIX = getenv('BASE_PREFIX', '!')
BASE_COLOR = Colour.from_rgb(241, 184, 19)
ERROR_COLOR = Colour.from_rgb(255, 0, 0)


@dataclass(order=True, slots=True)
class Track:
    url: str
    title: str
    thumbnail: str


class MusicHandlerBase(ABC):
    """
    Base class for music handlers.
    """

    @abstractmethod
    async def get_url(self, query: str) -> str:
        """
        Returns a url for the first video found using query passed.
        """
        raise NotImplementedError('Custom exception must have \'get_url\' method.')

    @abstractmethod
    async def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        """
        Returns a video url using query passed.
        """
        raise NotImplementedError('Custom exception must have \'get_urls\' method.')

    @abstractmethod
    async def get_metas(self, query: str, max_results: int = 5) -> list[Track]:
        """
        Gets query and returns information about the videos found.
        """
        raise NotImplementedError('Custom exception must have \'get_metas\' method.')

    @abstractmethod
    async def get_metadata(self, query: str, is_url: bool = False) -> tuple[Track]:
        """
        Gets query and returns information about the first video found.
        """
        raise NotImplementedError('Custom exception must have \'get_metadata\' method.')

    @abstractmethod
    async def get_stream(self, url: str) -> str:
        """
        Requires a video url to be passed as an argument.
        Returns a url to a stream of the video passed.
        """
        raise NotImplementedError('Custom exception must have \'get_stream\' method.')


class CustomException(commands.CommandError, ABC):
    """
    Base class for all the exceptions below
    """
    
    @abstractproperty
    def description(self) -> str:
        raise NotImplementedError('Custom exception must have \'description\' property.')
    
    @abstractproperty
    def type_(self) -> str:
        raise NotImplementedError('Custom exception must have \'type_\' property.')
