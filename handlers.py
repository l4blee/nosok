import asyncio
import re
import threading
from multiprocessing.pool import ThreadPool
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
        self._video_regex = re.compile(r'watch\?v=(\S{11})')

    def get_urls(self, query: str, max_results: int = 5) -> list:
        query = '+'.join(query.split(' '))

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        vid_ids = self._video_regex.findall(res.text)[:max_results]
        return [self._video_pattern + i for i in vid_ids]

    def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str]]:
        links = self.get_urls(query, max_results=max_results)
        args = [(i, False) for i in links]

        with ytdl(self._ydl_opts) as ydl:
            p: ThreadPool = ThreadPool(max_results)
            res = p.starmap(ydl.extract_info, args)

        res = [(self._video_pattern + i.get('id'), i.get('title')) for i in res]
        return res

    def get_info(self, query: str) -> tuple[str, str]:
        return self.get_infos(query, max_results=1)[0]

    @staticmethod
    def get_stream(url: str):
        streams = YouTube(url).streams.filter(type='audio')
        return max(streams, key=lambda x: x.bitrate).url
