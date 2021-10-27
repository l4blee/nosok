import asyncio
import json
import logging
import os
import re
import threading
import typing
from datetime import datetime, timedelta
from http import server
from multiprocessing.pool import ThreadPool

import requests
from discord.ext import commands
from googleapiclient.discovery import build
from pytube import YouTube
from youtube_dl import YoutubeDL as YtDL

from base import BASE_COLOR
from utils import send_embed


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
        query = '+'.join(query.split())

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        iterator = self._video_regex.finditer(res.text)
        return [self._video_pattern + next(iterator).group(1) for _ in range(max_results)]

    def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        links = self.get_urls(query, max_results=max_results)
        args = [(i, False) for i in links]

        with YtDL(self._ydl_opts) as ydl:
            p: ThreadPool = ThreadPool(max_results)
            res = p.starmap(ydl.extract_info, args)

        res = [(self._video_pattern + i.get('id'), i.get('title'), i.get('thumbnails')[0]['url']) for i in res]
        return res

    def get_info(self, query: str, is_url: bool=False) -> tuple[str, str]:
        if not is_url:
            query = '+'.join(query.split())
            with requests.Session() as session:
                res = session.get(self._search_pattern + query)

            _id = next(self._video_regex.finditer(res.text))
            url = self._video_pattern + _id.group(1)
        else:
            url = query

        with YtDL(self._ydl_opts) as ydl:
            title = ydl.extract_info(url, download=False).get('title')

        return url, title

    def get_stream(self, url: str):
        with YtDL(self._ydl_opts) as ydl:
            streams = ydl.extract_info(url, download=False).get('formats')

        return max([i for i in streams if i.get('fps') is None],
                   key=lambda x: x.get('tbr')).get('url')


class EventHandler:
    def __init__(self, bot):
        self._bot = bot
        self._loop = bot.loop
        self.to_check: dict = dict()

        asyncio.run_coroutine_threadsafe(self.loop(), self._loop)

    async def loop(self):
        while True:
            await self.checkall()
            await asyncio.sleep(100)

    def on_song_end(self, ctx: commands.Context):
        self.to_check[ctx] = datetime.now() + timedelta(minutes=5)

    def on_song_start(self, ctx: commands.Context):
        self.to_check[ctx] = None

    async def checkall(self):
        for i in self.to_check.keys():
            timestamp = self.to_check[i]
            if timestamp and datetime.now() >= timestamp:
                music_cog = self._bot.get_cog('Music')
                await music_cog.leave(i)
                self.to_check[i] = None
                await send_embed(
                    ctx=i,
                    description='I have been staying AFK for too long, so I left the channel',
                    color=BASE_COLOR
                )


class RequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        data = {
            'latency': '123'
        }
        self.wfile.write(
            json.dumps(data).encode('utf-8')
        )


class ConnectionHandler:
    def __init__(self, bot):
        self._bot = bot
        self._server = server.HTTPServer(
            ('localhost', 8000),
            RequestHandler
        )
        self.thread = threading.Thread(target=self._server.serve_forever, args=())

        self._logger = logging.getLogger('SERVER')

    def run(self):
        self._logger.info('Starting ConnectionHandler')
        self._logger.info('Launching server\'s thread')
        self.thread.start()
        self._logger.info('Server has been started successfully')
