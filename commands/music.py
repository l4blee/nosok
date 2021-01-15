from youtube_dl import YoutubeDL
import discord
from collections import defaultdict
import asyncio
from subprocess import DEVNULL
from os import getenv

DELETE_DELAY = float(getenv('DELETE_DELAY'))
YTDL_OPTS = {
    'format': 'worstaudio/worst',
    'quiet': True
}


class QueueElement(object):
    def __init__(self, title: str, url: str, added_by: discord.Member.mention):
        self.title = title
        self.url = url
        self.added_by = added_by


class SongQueue(object):
    __queue = list()

    def __init__(self):
        self.repeat = False
        self.play_after = True
        self.volume = 1
        self.now_playing = -1

    def add_song(self, title: str, url: str, mentionable: discord.Member.mention):
        song = QueueElement(title, url, mentionable)
        self.__queue.append(song)

    def remove_song(self, index: int):
        if 0 <= index < len(self.__queue):
            return self.__queue.pop(index)
        else:
            raise IndexError('Incorrect index given')

    def __next__(self):
        if not self.__queue:
            return None

        self.now_playing += 1
        if self.now_playing >= len(self.__queue):
            self.now_playing = -1
            if not self.repeat:
                return -1

        return self.__queue[self.now_playing]

    def __len__(self):
        return len(self.__queue)

    def __getitem__(self, item):
        return self.__queue[item]


class MusicClient(object):
    def __init__(self, client, ytdl_opts: dict = None):
        self.YTDL_OPTS = ytdl_opts
        self.client = client
        self.aliases = defaultdict(list)
        self.commands = list()
        self.queues = defaultdict(SongQueue)

    def command(self, aliases: list = None):
        aliases = aliases or list()

        def decorator(coro):
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError('Provided function must be a coroutine')

            setattr(self, coro.__name__, coro)
            for name in aliases:
                setattr(self, name, coro)

            return coro
        return decorator

    def get_voice_instance(self, guild_id: discord.Guild.id):
        for voice_client in self.client.voice_clients:
            if voice_client.guild.id == guild_id:
                return voice_client
        else:
            return None

    def create_ytdl_source(self, source_url: str):
        info = YoutubeDL(self.YTDL_OPTS).extract_info(source_url, download=False)
        return discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            info['formats'][0]['url'],
            stderr=DEVNULL,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        ), info
