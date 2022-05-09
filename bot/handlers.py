import os
import asyncio
from datetime import datetime, timedelta
from json import dump
from logging import getLogger
# from multiprocessing.pool import ThreadPool
from re import compile as comp_
from threading import Thread, Event
from time import sleep
from psutil import Process

import requests
from discord.ext import commands
import discord
from yt_dlp import YoutubeDL as YtDL

from base import BASE_COLOR, MusicHandlerBase
from utils import send_embed


class YDLHandler(MusicHandlerBase):
    def __init__(self, ydl_opts: dict, scheme: str = 'https'):
        self._ydl_opts = ydl_opts
        self._scheme = scheme
        self._search_pattern = scheme + '://www.youtube.com/results?search_query='
        self._video_pattern = scheme + '://www.youtube.com/watch?v='
        self._video_regex = comp_(r'watch\?v=(\S{11})')

    async def get_url(self, query: str) -> str:  # video url
        query = '+'.join(query.split())

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        iterator = self._video_regex.finditer(res.text)
        return self._video_pattern + next(iterator).group(1)

    async def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        query = '+'.join(query.split())

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        iterator = self._video_regex.finditer(res.text)
        return [self._video_pattern + next(iterator).group(1) for _ in range(max_results)]

    async def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        links = await self.get_urls(query, max_results=max_results)

        with YtDL(self._ydl_opts) as ydl:
            reqs = [asyncio.to_thread(ydl.extract_info, i) for i in links]

        return [
            (self._video_pattern + result.get('id'), 
                result.get('title'), 
                result.get('thumbnails')[0]['url'])
            for result in await asyncio.gather(*reqs)
        ]

        # The code below seems to work a bit faster, need proper testing

        # args = [(i, False) for i in links]  # link, download=False

        # with YtDL(self._ydl_opts) as ydl:
        #     p: ThreadPool = ThreadPool(max_results)
        #     res = p.starmap(ydl.extract_info, args)

        # res = [(self._video_pattern + i.get('id'), i.get('title'), i.get('thumbnails')[0]['url']) for i in res]
        # return res

    async def get_info(self, query: str, is_url: bool = False) -> tuple[str, str]:
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

    async def get_stream(self, url: str):
        with YtDL(self._ydl_opts) as ydl:
            streams = ydl.extract_info(url, download=False).get('formats')

        streams = [i for i in streams if i.get('audio_ext') != 'none']
        return max([i for i in streams if i.get('fps') is None],
                   key=lambda x: x.get('tbr')).get('url')


class EventHandler(Thread):
    def __init__(self, bot):
        super().__init__(target=self.loop,
                         daemon=True)
        self._stop = Event()

        self._bot = bot
        self.to_check: dict = dict()

    def loop(self):
        while 1:
            asyncio.run_coroutine_threadsafe(self.checkall(), self._bot.loop)
            sleep(60)

    def on_song_end(self, ctx: commands.Context):
        self.to_check[ctx] = datetime.now() + timedelta(minutes=5)

    def on_song_start(self, ctx: commands.Context):
        if ctx in self.to_check:
            del self.to_check[ctx]

    '''async def on_message(self, message: discord.Message):
        ctx = await self._bot.get_context(message)
        self.to_check[ctx] = message'''

    async def checkall(self):
        for ctx, timestamp in self.to_check.items():
            player = ctx.voice_client
            if not player:
                del self.to_check[ctx]
                continue

            if player.is_playing():
                del self.to_check[ctx]
                continue

            if timestamp and datetime.now().time() >= timestamp.time():
                await player.disconnect()

                del self.to_check[ctx]

                await send_embed(
                    ctx=ctx,
                    description='I have been staying AFK for too long, so I left the voice channel',
                    color=BASE_COLOR
                )

    def stopped(self):
        return self._stop.is_set()

    def close(self):
        self._stop.set()


class DataProcessor(Thread):
    __slots__ = ('_bot', '_logger', '_stop')

    def __init__(self, bot):
        super().__init__(target=self.loop,
                         daemon=True)
        self._stop = Event()

        self._bot = bot
        self._logger = getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)

    def loop(self):
        while 1:
            self.read_and_collect()
            sleep(5)
    
    def read_and_collect(self):
        this_proc = Process()

        voices = [i.voice_client for i in self._bot.guilds]
        procs = [i.source.original._process
                    for i in voices
                    if i and i.source]
        cpu_utils = 0
        mem_utils = 0

        for i in filter(bool, procs):
            proc = Process(i.pid)

            cpu_utils += proc.cpu_percent()
            mem_utils += round(proc.memory_info().rss / float(10 ** 6), 2)

        cpu_usage = this_proc.cpu_percent() + cpu_utils
        mem_usage = round(this_proc.memory_info().rss / (10 ** 6), 2) + mem_utils

        with open(f'{os.getcwd() + "/bot/data/data.json"}', 'w') as f:
            data = {
                'status': 'online',
                'vars': {
                    'servers': len(self.bot.guilds),
                    'cpu_used': cpu_usage,
                    'memory_used': str(mem_usage) + 'M'
                },
                'last_updated': datetime.now().strftime('%d.%b.%Y %H:%M:%S')
            }

            dump(data, f, indent=4)

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
