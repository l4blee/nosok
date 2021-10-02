import re
import typing

import requests
from googleapiclient.discovery import build
from pytube import YouTube
from youtube_dl import YoutubeDL as ytdl


class YTAPIHandler:
    def __init__(self, api_key: str, scheme: str = 'https'):
        self._scheme = scheme
        self._service = build('youtube', 'v3', developerKey=api_key)
        self._video_pattern = scheme + '://www.youtube.com/watch?v='

    def get_infos(self, query: str, max_results: int = 5) -> typing.Generator:
        response = self._service.search().list(
            q=query,
            part='id, snippet',
            maxResults=max_results).execute()

        for i in response.get('items'):
            yield self._video_pattern + i['id']['videoId'], i['snippet']['title']  # url, info

    def get_info(self, query: str) -> tuple[str, str]:
        return next(self.get_infos(query))

    @staticmethod
    def get_stream(url) -> str:
        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url


class YDLHandler:
    def __init__(self, ydl_opts: dict, scheme: str = 'https'):
        self._ydl_opts = ydl_opts
        self._scheme = scheme
        self._search_pattern = scheme + '://www.youtube.com/results?search_query='
        self._video_pattern = scheme + '://www.youtube.com/watch?v='

    def get_urls(self, query: str, max_results: int = 5) -> list:
        with requests.Session() as session:
            query = '+'.join(query.split(' '))
            res = session.get(self._search_pattern + query)

        ids = re.findall(r'watch\?v=(\S{11})', res.text)[:max_results]
        return [self._video_pattern + i for i in ids]

    def get_infos(self, query: str, max_results: int = 5) -> typing.Generator:
        with ytdl(self._ydl_opts) as ydl:
            links = self.get_urls(query, max_results=max_results)
            for url in links:
                yield url, ydl.extract_info(url, download=False)['title']

    def get_info(self, query: str) -> tuple[str, str]:
        return next(self.get_infos(query))

    @staticmethod
    def get_stream(url: str):
        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url
