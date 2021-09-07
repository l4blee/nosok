import discord
from discord.ext import commands


class EndOfQueue(Exception):
    pass


class Queue:
    def __init__(self):
        self._tracks: list[tuple] = []
        self._loop: int = 0  # 0 - None; 1 - Current queue; 2 - Current track
        self._now_playing: int = 0

    def add(self, url: str, title: str, mention: discord.User.mention) -> None:
        self._tracks.append((url, title, mention))

    def get_next(self) -> tuple:
        self._now_playing += int(self._loop != 2)
        if self._now_playing > len(self._tracks):
            if self._loop == 1:
                raise EndOfQueue
            else:
                self._now_playing = 0

        return self._tracks[self._now_playing]

    def remove(self, index: int) -> None:
        self._tracks.pop(index)

    @property
    def queue(self) -> list:
        return self._tracks


class Music(commands.Cog):
    def __init__(self):
        self._queues: list[Queue] = []

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context) -> None:
        if ctx.guild.voice_client:
            await ctx.channel.send('Already connected')
            return
        voice = ctx.author.voice
        if not voice:
            await ctx.channel.send('Connect first')
            return
        await voice.channel.connect()


music = Music()
