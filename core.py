import os
import typing

import sqlalchemy as sa
from googleapiclient.discovery import build
from pytube import YouTube
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

    def get_urls(self, query: str, max_results: int = 5) -> typing.Generator:
        response = self._service.search().list(
            q=query,
            part='id, snippet',
            maxResults=max_results).execute()

        for i in response.get('items'):
            yield self._scheme + '://youtube.com/watch?v=' + i['id']['videoId'], i['snippet']  # url, info

    def get_url(self, query: str) -> tuple:
        return next(self.get_urls(query))

    def get_stream(self, query: str = '', url: str = '') -> str:
        if not query and not url:
            raise ValueError('Neither query nor url given')

        if not url:
            url = self.get_url(query)[0]

        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url


google_api_token = os.environ.get('GOOGLE_API_TOKEN')
yt_handler = YoutubeHandler(google_api_token)
Session = sessionmaker(bind=engine)
