import asyncio
import json
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta
from http import server
from multiprocessing.pool import ThreadPool

import requests
from discord.ext import commands
from psutil import Process
from youtube_dl import YoutubeDL as YtDL

from base import BASE_COLOR
from utils import send_embed


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

    def get_info(self, query: str, is_url: bool = False) -> tuple[str, str]:
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
        self.to_check: dict = dict()

        asyncio.run_coroutine_threadsafe(self.loop(), bot.loop)

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
            if timestamp and \
                    datetime.now() >= timestamp and \
                    not i.voice_client.is_playing():
                music_cog = self._bot.get_cog('Music')
                await music_cog.leave(i)
                self.to_check[i] = None
                await send_embed(
                    ctx=i,
                    description='I have been staying AFK for too long, so I left the channel',
                    color=BASE_COLOR
                )


class DataProcessor(threading.Thread):
    def __init__(self, bot):
        super().__init__(target=self.loop,
                         daemon=True)
        self._stop = threading.Event()

        self._bot = bot
        self._logger = logging.getLogger('DataProcessor')

    def loop(self):
        while True:
            with open(f'{os.getcwd() + "/bot/data.json"}', 'w') as f:
                data = {
                    'status': 'online',
                    'vars': {
                        'servers': [i.id for i in self.bot.guilds],
                        'latency': self.bot.latency,
                        'memory_used': Process(os.getpid()).memory_info().rss / (1024 * 1024)
                    }
                }

                json.dump(data, f, indent=4)
            time.sleep(5)

    @property
    def bot(self):
        return self._bot

    def start(self) -> None:
        self._logger.info('Launching Data Processor\'s thread...')
        super().start()

    def stopped(self):
        return self._stop.is_set()

    def close(self):
        self._logger.info('Closing Data Processor...')
        self._stop.set()
