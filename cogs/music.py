import discord
from discord.ext import commands
from collections import defaultdict
from core import yt_handler as _yt
import asyncio


class EndOfQueue(Exception):
    pass


class Queue:
    def __init__(self):
        self._tracks: list[tuple] = []
        self._loop: int = 0  # 0 - None; 1 - Current queue; 2 - Current track
        self._now_playing: int = 0
        self.play_next: bool = True

    def add(self, url: str, title: str, mention: discord.User.mention) -> None:
        self._tracks.append((url, title, mention))

    def get_next(self) -> tuple:
        ret = self._tracks[self._now_playing]

        self._now_playing += int(self._loop != 2)
        if self._now_playing > len(self._tracks):
            if self._loop == 1:
                raise EndOfQueue
            else:
                self._now_playing = 0

        return ret

    def remove(self, index: int) -> None:
        self._tracks.pop(index)

    @property
    def is_empty(self) -> bool:
        return not bool(self._tracks)

    @property
    def queue(self) -> list:
        return self._tracks


class Music(commands.Cog):
    def __init__(self):
        self._queues: defaultdict[Queue] = defaultdict(Queue)

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel) -> None:
        if ctx.voice_client:
            await ctx.channel.send('Already connected')
            return

        voice = ctx.author.voice

        if not voice:
            await ctx.channel.send('Connect first')
            return

        if voice_channel:
            await voice_channel.connect()
        else:
            voice.channel.connect()

    @commands.command(aliases=['l'])
    async def leave(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            await ctx.channel.send('Not connected yet')
            return
        if voice.is_playing():
            await self.stop(ctx)
        await voice.disconnect()

    @commands.command(aliases=['s'])
    async def stop(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            await ctx.channel.send('Not connected yet')
            return

        q = self._queues[ctx.guild.id]
        q.play_next = False
        voice.stop()

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice:
                await ctx.channel.send('Connect first')
                return

            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        args = ctx.message.content.split(' ')[1:]
        if args:
            if voice.is_playing():
                await self.queue(ctx)
                return

            if voice.is_paused():
                await voice.resume()
                return

            query = ' '.join(args)
            stream = _yt.get_stream(query=query)
            voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(stream, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')))
        else:
            if voice.is_paused():
                await voice.resume()
                return

            if not q.is_empty:
                url, title, mention = q.get_next()
            else:
                await ctx.channel.send('No songs left')
                return

            stream = _yt.get_stream(url=url)
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(stream)),
                       after=lambda _: self._after(ctx, loop))

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if not q.play_next:
            res = asyncio.run_coroutine_threadsafe(self.play(ctx), loop)

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context) -> None:
        q: Queue = self._queues[ctx.guild.id]
        args = ctx.message.content.split(' ')[1:]
        if args:
            query = ' '.join(args)
            url, info = _yt.get_url(query)
            q.add(url, info['title'], ctx.author.mention)

            embed = discord.Embed(description=f'Queued: [{info["title"]}]({url})',
                                  color=discord.Colour.from_rgb(255, 255, 255))
            await ctx.channel.send(embed=embed)
        else:
            desc = ''
            for url, title, mention in q.queue:
                desc += f'[{title}]({url}) | {mention}\n'

            embed = discord.Embed(title='Current queue:',
                                  color=discord.Colour.from_rgb(255, 255, 255),
                                  description=desc)
            await ctx.channel.send(embed=embed)


music = Music()
