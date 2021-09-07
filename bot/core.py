import os

import peewee
from googleapiclient.discovery import build
from pytube import YouTube
import typing

name = os.getenv('db-name')
host = os.getenv('db-host')
port = int(os.getenv('db-port'))
user = os.getenv('db-username')
password = os.getenv('db-password')
google_api_token = os.getenv('google-api-token')

db = peewee.MySQLDatabase(name,
                          host=host,
                          port=port,
                          user=user,
                          password=password)


class Config(peewee.Model):
    guild_id = peewee.IntegerField(unique=True)
    prefix = peewee.CharField()

    class Meta:
        database = db


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
        return self.get_urls(query).__next__()

    def get_stream(self, query: str = '', url: str = '') -> str:
        if not query and not url:
            raise ValueError('Neither query nor url given')

        if not url:
            url = self.get_url(query)[0]

        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url


config = Config()
config.create_table()

yt_handler = YoutubeHandler(google_api_token)
