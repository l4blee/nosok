import os
from asyncio import run_coroutine_threadsafe
from gc import collect
from datetime import datetime, timedelta
from json import dump
from logging import getLogger
from multiprocessing.pool import ThreadPool
from re import compile
from threading import Thread, Event
from time import sleep
import psutil

import requests
from discord.ext import commands
import discord
from soundcloud import SoundCloud
from yt_dlp import YoutubeDL as YtDL

from base import BASE_COLOR, MusicHandlerBase
from utils import send_embed


class YDLHandler(MusicHandlerBase):
    def __init__(self, ydl_opts: dict, scheme: str = 'https'):
        self._ydl_opts = ydl_opts
        self._scheme = scheme
        self._search_pattern = scheme + '://www.youtube.com/results?search_query='
        self._video_pattern = scheme + '://www.youtube.com/watch?v='
        self._video_regex = compile(r'watch\?v=(\S{11})')

    def get_url(self, query: str) -> str:
        query = '+'.join(query.split())

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        iterator = self._video_regex.finditer(res.text)
        return self._video_pattern + next(iterator).group(1)

    def get_urls(self, query: str, max_results: int = 5) -> list:
        query = '+'.join(query.split())

        with requests.Session() as session:
            res = session.get(self._search_pattern + query)

        iterator = self._video_regex.finditer(res.text)
        return [self._video_pattern + next(iterator).group(1) for _ in range(max_results)]

    def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        links = self.get_urls(query, max_results=max_results)
        args = [(i, False) for i in links]  # link, download=False

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

        streams = [i for i in streams if i.get('audio_ext') != 'none']
        return max([i for i in streams if i.get('fps') is None],
                   key=lambda x: x.get('tbr')).get('url')


class SCHandler(MusicHandlerBase):
    def __init__(self):
        self.client = SoundCloud(os.environ.get('CLIENT_ID'))

    def get_url(self, query: str) -> str:
        return next(self.client.search_tracks(query)).permalink_url

    def get_urls(self, query: str, max_results: int = 5) -> list[str]:
        return [next(self.client.search_tracks(query)).permalink_url for _ in range(max_results)]

    def get_infos(self, query: str, max_results: int = 5) -> list[tuple[str, str, str]]:
        data = self.client.search_tracks(query)
        output = []
        for _ in range(max_results):
            track = next(data)
            output.append((track.permalink_url, track.title, track.artwork_url))

        return output

    def get_info(self, query: str, is_url: bool = False) -> tuple[str, str]:
        if not is_url:
            track = next(self.client.search_tracks(query))
        else:
            track = self.client.resolve(query)

        return track.permalink_url, track.title

    def get_stream(self, url: str) -> str:
        track = self.client.resolve(url)
        url = [i for i in track.media.transcodings if i.format.mime_type == 'audio/mpeg'][0].url

        headers = self.client.get_default_headers()
        if self.client.auth_token:
            headers['Authentication'] = f'OAuth {self.client.auth_token}'

        res = requests.get(url, params={'client_id': self.client.client_id}, headers=headers)
        res.raise_for_status()
        return res.json()['url']


class EventHandler:
    def __init__(self, bot):
        self._bot = bot
        self.to_check: dict = dict()
        self._logger = getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)

        self._thread = Thread(target=self.loop,
                              daemon=True)
        self._thread.start()


    def loop(self):
        while 1:
            self._logger.info('Initiating guilds check and garbage collecting...')
            collect()
            run_coroutine_threadsafe(self.checkall(), self._bot.loop)
            sleep(60)

    def on_song_end(self, ctx: commands.Context):
        self.to_check[ctx] = datetime.now() + timedelta(minutes=5)

    def on_song_start(self, ctx: commands.Context):
        self.to_check[ctx] = None

    async def checkall(self):
        for ctx, timestamp in self.to_check.items():
            player = ctx.voice_client
            if not player:
                self.to_check[ctx] = None
                continue

            if player.is_playing():
                self.to_check[ctx] = None
                continue

            if timestamp and datetime.now().time() >= timestamp.time():
                await player.disconnect()
                player.cleanup()
                del player

                self.to_check[ctx] = None

                await send_embed(
                    ctx=ctx,
                    description='I have been staying AFK for too long, so I left the voice channel',
                    color=BASE_COLOR
                )


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
        this_proc = psutil.Process()

        voices = [i.voice_client for i in self._bot.guilds]
        procs = [i.source.original._process
                    for i in voices
                    if i and i.source]  # Get procs
        cpu_utils = 0
        mem_utils = 0

        for i in filter(bool, procs):
            try:
                proc = psutil.Process(i.pid)

                cpu_utils += proc.cpu_percent()
                mem_utils += round(proc.memory_info().rss / float(10 ** 6), 2)
            except Exception as e:
                self._logger.exception(e, exc_info=True)

        cpu_usage = this_proc.cpu_percent() + cpu_utils
        mem_usage = round(this_proc.memory_info().rss / (10 ** 6), 2) + mem_utils

        with open(f'{os.getcwd() + "/bot/data/data.json"}', 'w') as f:
            data = {
                'status': 'online',
                'vars': {
                    'servers': len(self.bot.guilds),
                    'cpu_used': cpu_usage,
                    'memory_used': str(mem_usage) + 'M'
                }
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
