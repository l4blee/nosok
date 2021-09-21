import asyncio
from collections import defaultdict

import discord
from discord.ext import commands

from core import yt_handler as _yt


class EndOfQueue(Exception):
    pass


class Queue:
    def __init__(self):
        self._tracks: list[tuple] = []
        self._loop: int = 1  # 0 - None; 1 - Current queue; 2 - Current track
        self.now_playing: int = 0 # even if there's only one track in the queue it's equals 1. Why?
        self.play_next: bool = True

    def add(self, url: str, title: str, mention: discord.User.mention) -> None:
        self._tracks.append((url, title, mention))

    def get_next(self) -> tuple:
        if self.now_playing >= len(self._tracks):
            if self._loop == 0:
                self.now_playing = 0
                self.play_next = False
                return ()
            else:
                self.now_playing = 0

        ret = self._tracks[self.now_playing]
        self.now_playing += int(self._loop != 2)

        return ret

    def remove(self, index: int) -> None:
        self._tracks.pop(index)

    def clear(self) -> None:
        self._tracks = []

    @property
    def is_empty(self) -> bool:
        return not bool(self._tracks)

    @property
    def queue(self) -> list:
        return self._tracks

    @property
    def current(self):
        return self._tracks[self.now_playing - 1]


class Music(commands.Cog):
    def __init__(self):
        self._queues: defaultdict[Queue] = defaultdict(Queue)

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel = None) -> None:
        if ctx.voice_client:
            await ctx.send('Already connected')
            return

        voice = ctx.author.voice

        if not voice:
            await ctx.send('Connect first')
            return

        if voice_channel:
            await voice_channel.connect()
        else:
            voice.channel.connect()

    @commands.command(aliases=['l'])
    async def leave(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return
        if voice.is_playing():
            await self.stop(ctx)
        await voice.disconnect()

    @commands.command(aliases=['s'])
    async def stop(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return

        q = self._queues[ctx.guild.id]
        q.play_next = False
        voice.stop()

    @commands.command(aliases=['ps'])
    async def pause(self, ctx: commands.Context) -> None:
        """
        Pauses the current song. You can resume, just by typing `!p`.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return

        if voice.is_playing():
            voice.pause()

    @commands.command(aliases=['left'])
    async def continue_where_left_off(self, ctx: commands.Context): # TODO: finish it
        """
        Pauses the song in its current length. When you levave the voice channel,
        you can resume where you left off.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return

    @commands.command(aliases=['c'])
    async def current(self, ctx: commands.Context) -> None:
        """
        Displays the current song.
        """
        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        current = q.current

        if not voice:
            await ctx.send('No songs are playing')
            return
        
        embed = discord.Embed(
            title='The current song',
            description=current[1],
            url=current[0],
            colour=discord.Color.from_rgb(255, 0, 0)
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context) -> None:
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice:
                await ctx.send('Connect first')
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
            url, info = _yt.get_url(query)
            q.add(url, info['title'], ctx.author.mention)
            q.now_playing += 1

            stream = _yt.get_stream(url=url)
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream,
                                       before_options='-reconnect 1'
                                                      ' -reconnect_streamed 1'
                                                      ' -reconnect_delay_max 5')),
                after=lambda _: self._after(ctx, loop))
        else:
            if voice.is_paused():
                voice.resume()
                return

            if not q.is_empty:
                res = q.get_next()
                if res == ():
                    await ctx.send('Queue ended')
                    return
                else:
                    url, title, mention = res
            else:
                await ctx.send('No songs left')
                return

            stream = _yt.get_stream(url=url)
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream,
                                       before_options='-reconnect 1'
                                                      ' -reconnect_streamed 1'
                                                      ' -reconnect_delay_max 5')),
                after=lambda _: self._after(ctx, loop))

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if q.play_next:
            ctx.message.content = ''
            return asyncio.run_coroutine_threadsafe(self.play(ctx), loop)

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
            await ctx.send(embed=embed)
        else:
            desc = ''
            for url, title, mention in q.queue:
                desc += f'[{title}]({url}) | {mention}\n'

            embed = discord.Embed(title='Current queue:',
                                  color=discord.Colour.from_rgb(255, 255, 255),
                                  description=desc)
            await ctx.send(embed=embed)

    @commands.command(aliases=['clr'])
    async def clear(self, ctx: commands.Context):
        q = self._queues[ctx.guild.id]
        q.clear()

    @commands.command()
    async def loop(self, cxt: commands.Context):
        q = self._queues[cxt.guild.id]
        q._loop += 1
        if q._loop > 2:
            q._loop = 0

        loop_setting = ['None', 'Current queue', 'Current track'][q._loop]
        await cxt.send(f'Now looping is set to: `{loop_setting}`')
