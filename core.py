import re

import requests
import sqlalchemy as sa
import youtube_dl
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker

from base import Base, engine
from config import config


class Config(Base):
    __tablename__ = 'config'

    guild_id = sa.Column('guild_id', sa.BigInteger, unique=True, primary_key=True)
    prefix = sa.Column('prefix', sa.String, server_default='!')


class YoutubeHandler:
    def __init__(self, scheme: str = 'https'):
        self._scheme = scheme

    def get_tracks(self, query: tuple, max_number: int = 5) -> list[tuple]:
        """
        Gets a tuple containing the song's url and the title.
        """
        response = requests.get(f"{self._scheme}://www.youtube.com/results?search_query={'+'.join(query)}&sp=EgIQAQ%253D%253D")
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)[:max_number]
        video_titles = []
        for v in video_ids:
            video_titles.append(BeautifulSoup(requests.get(f'https://www.youtube.com/watch?v={v}').text, 'html.parser').find('meta', property='og:title')['content'])

        tracks: list[tuple] = []
        for i in range(max_number):
            tracks.append((f'https://www.youtube.com/watch?v={video_ids[i]}', video_titles[i]))

        return tracks

    def get_track(self, query: tuple, max_number: int = 5) -> tuple:
        return self.get_tracks(query, max_number)[0]

    @staticmethod
    def get_stream(url: str) -> str:
        with youtube_dl.YoutubeDL(config.YDL_OPTS) as ydl:
            return ydl.extract_info(url, download=False).get('url')


yt_handler = YoutubeHandler()
Session = sessionmaker(bind=engine)
