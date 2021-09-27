import os
import typing

<<<<<<< HEAD
import requests
import sqlalchemy as sa
import youtube_dl
from bs4 import BeautifulSoup
=======
import discord
import sqlalchemy as sa
from googleapiclient.discovery import build
from pytube import YouTube
>>>>>>> parent of 79cb644 (Rewrite YoutubeHandler to make it work with the `youtube-dl` library, add config.py and utils.py)
from sqlalchemy.orm import sessionmaker

from base import Base, engine


class Config(Base):
    __tablename__ = 'config'

    guild_id = sa.Column('guild_id', sa.BigInteger, unique=True, primary_key=True)
    prefix = sa.Column('prefix', sa.String, server_default='!')


class YoutubeHandler:
    def __init__(self, api_key: str, scheme: str = 'https'):
        self._scheme = scheme
        self._service = build('youtube', 'v3', developerKey=api_key)

<<<<<<< HEAD
    def get_tracks(self, query: tuple, max_number: int = 5) -> list[tuple]:
        """
        Gets a tuple containing the song's url and the title.
        """
        response = requests.get(f"{self._scheme}://www.youtube.com/results?search_query={'+'.join(query)}&sp=EgIQAQ%253D%253D")
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)[:max_number]
        video_titles = []
        for v in video_ids:
            video_titles.append(BeautifulSoup(requests.get(f'https://www.youtube.com/watch?v={v}').text, 'html.parser').find('meta', property='og:title')['content'])
=======
    def get_urls(self, query: str, max_results: int = 5) -> typing.Generator:
        response = self._service.search().list(
            q=query,
            part='id, snippet',
            maxResults=max_results).execute()
>>>>>>> parent of 79cb644 (Rewrite YoutubeHandler to make it work with the `youtube-dl` library, add config.py and utils.py)

        for i in response.get('items'):
            yield self._scheme + '://youtube.com/watch?v=' + i['id']['videoId'], i['snippet']  # url, info

    def get_url(self, query: str) -> tuple:
        return next(self.get_urls(query))

<<<<<<< HEAD
    def get_track(self, query: tuple, max_number: int = 5) -> tuple:
        return self.get_tracks(query, max_number)[0]

    @staticmethod
    def get_stream(url: str) -> str:
        with youtube_dl.YoutubeDL(config.YDL_OPTS) as ydl:
            return ydl.extract_info(url, download=False).get('url')
=======
    def get_stream(self, query: str = '', url: str = '') -> str:
        if not query and not url:
            raise ValueError('Neither query nor url given')
>>>>>>> parent of 79cb644 (Rewrite YoutubeHandler to make it work with the `youtube-dl` library, add config.py and utils.py)

        if not url:
            url = self.get_url(query)[0]

        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url


google_api_token = os.environ.get('GOOGLE_API_TOKEN')
yt_handler = YoutubeHandler(google_api_token)
Session = sessionmaker(bind=engine)
