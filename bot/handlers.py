import asyncio
from urllib.parse import urlparse, parse_qs
from os import getcwd
from datetime import datetime, timedelta
from json import dump
from logging import getLogger
# from multiprocessing.pool import ThreadPool
from re import compile as comp_
from threading import Thread, Event
from time import sleep
from psutil import Process
from dataclasses import dataclass

import aiohttp
from discord.ext import commands
import discord
from yt_dlp import YoutubeDL as YtDL

from base import BASE_COLOR, MusicHandlerBase, Track
from utils import send_embed
from languages import get_phrase


class YDLHandler(MusicHandlerBase):
    def __init__(self, ydl_opts: dict, scheme: str = 'https'):
        self._ydl_opts = ydl_opts
        self._scheme = scheme

        # Consts
        self._search_pattern = scheme + '://www.youtube.com/results?search_query='
        self._video_pattern = scheme + '://www.youtube.com/watch?v='
        self._video_regex = comp_(r'watch\?v=(\S{11})')

    async def get_url(self, query: str) -> str:  # video url
        async with aiohttp.ClientSession() as session:
            async with session.get(self._search_pattern + query.replace(' ', '+')) as res:
                iterator = self._video_regex.finditer(await res.text())

        return self._video_pattern + next(iterator).group(1)

    async def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self._search_pattern + query.replace(' ', '+')) as res:
                iterator = self._video_regex.finditer(await res.text())

        return [self._video_pattern + next(iterator).group(1) for _ in range(max_results)]

    async def get_metas(self, query: str, max_results: int = 5) -> list[Track]:
        links = await self.get_urls(query, max_results=max_results)

        with YtDL(self._ydl_opts) as ydl:
            reqs = [asyncio.to_thread(ydl.extract_info, i) for i in links]

        return [
            Track(self._video_pattern + result.get('id'), 
                  result.get('title'), 
                  result.get('thumbnails')[0]['url'])
            for result in await asyncio.gather(*reqs)
        ]

    async def get_metadata(self, query: str, is_url: bool = False) -> Track:
        if not is_url:
            url = self.get_url(query)
        else:
            # Simple additional query parameters bypass
            parsed = urlparse(query)
            video_id = parse_qs(parsed.query)['v'][0]
            # Getting proper URL to a video
            url = self._video_pattern + video_id

        with YtDL(self._ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)
            title, thumbnail = data.get('title'), data.get('thumbnails')[0]['url']

        return Track(url, title, thumbnail)

    async def get_stream(self, url: str):
        with YtDL(self._ydl_opts) as ydl:
            streams = ydl.extract_info(url, download=False).get('formats')

        streams = [i for i in streams if i.get('audio_ext') != 'none']
        return max([i for i in streams if i.get('fps') is None],
                   key=lambda x: x.get('tbr')).get('url')


class EventHandler(Thread):
    __slots__ = ('_bot', '_logger', '_stop', 'to_check')

    def __init__(self, bot):
        super().__init__(target=self.loop,
                         daemon=True)
        self._stop = Event()

        self._bot = bot
        self.to_check: dict = dict()
        self._logger = getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)

    def loop(self):
        while 1:
            asyncio.run_coroutine_threadsafe(self.checkall(), self._bot.loop)
            sleep(60)

    def on_song_end(self, ctx: commands.Context):
        self.to_check[ctx] = datetime.now() + timedelta(minutes=5)

    def on_song_start(self, ctx: commands.Context):
        if ctx in self.to_check:
            del self.to_check[ctx]

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
                    description=await get_phrase(ctx, 'afk'),
                    color=BASE_COLOR
                )

    def start(self) -> None:
        self._logger.info('Launching Event Handler\'s thread...')
        super().start()

    def stopped(self):
        return self._stop.is_set()

    def close(self):
        self._logger.info('Closing Event Handler...')
        self._stop.set()


class PerformanceProcessor(Thread):
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

        with open(f'{getcwd() + "/bot/data/data.json"}', 'w') as f:
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
        self._logger.info('Launching Performance Processor\'s thread...')
        super().start()

    def stopped(self):
        return self._stop.is_set()

    def close(self):
        self._logger.info('Closing Performance Processor...')
        self._stop.set()
