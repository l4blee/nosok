import asyncio
import typing
from collections import defaultdict

import discord
from discord.ext import commands

from core import yt_handler as _yt
from base import BASE_COLOR


class Queue:
    def __init__(self):
        self._tracks: list[tuple] = []
        self._loop: int = 0  # 0 - None; 1 - Current queue; 2 - Current track
        self.now_playing: int = 0
        self.play_next: bool = True

    def add(self, url: str, title: str, mention: discord.User.mention) -> None:
        self._tracks.append((url, title, mention))

    def get_next(self) -> typing.Any[tuple, None]:
        if self.now_playing >= len(self._tracks):
            if self._loop == 0:
                self.now_playing = 0
                self.play_next = False
                return None
            else:
                self.now_playing = 0

        ret = self._tracks[self.now_playing]
        self.now_playing += int(self._loop != 2)

        return ret

    def __len__(self):
        return len(self._tracks)

    def remove(self, index: int) -> tuple:
        return self._tracks.pop(index)

    def clear(self) -> None:
        self._tracks = []

    @property
    def is_empty(self) -> bool:
        return not bool(self._tracks)

    @property
    def queue(self) -> list:
        return self._tracks

    @property
    def current(self) -> typing.Any[tuple, None]:
        return self._tracks[self.now_playing - 1] if len(self._tracks) > 0 else None


class Music(commands.Cog):
    def __init__(self):
        self._queues: defaultdict[Queue] = defaultdict(Queue)

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel = None) -> None:
        """
        Makes the bot join your current voice channel
        """

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
        """
        Makes bot leave your current channel.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return
        if voice.is_playing():
            await self.stop(ctx)
        await voice.disconnect()

    @commands.command(aliases=['s'])
    async def stop(self, ctx: commands.Context) -> None:
        """
        Stops bot from playing current song.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return

        q = self._queues[ctx.guild.id]
        q.play_next = False
        q.now_playing += 1
        voice.stop()

    @commands.command(aliases=['ps'])
    async def pause(self, ctx: commands.Context) -> None:
        """
        Pauses current song. Use `play` command to resume.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return

        if voice.is_playing():
            voice.pause()

    '''@commands.command(aliases=['left'])
    async def continue_where_left_off(self, ctx: commands.Context):  # TODO: finish it
        # Made this private not to appear in help command, temporary ofc
        """
        Pauses the song in its current length. When you leave the voice channel,
        you can resume where you left off.
        """
        voice = ctx.voice_client
        if not voice:
            await ctx.send('Not connected yet')
            return'''

    @commands.command(aliases=['c'])
    async def current(self, ctx: commands.Context) -> None:
        """
        Displays current playing song.
        """
        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        current = q.current

        if not voice:
            await ctx.send('Not connected')
            return

        if not voice.is_playing():
            await ctx.send('Not playing now')
            return

        embed = discord.Embed(
            title='Current song:',
            description=f'[{current[1]}]({current[0]}) | {current[2]}',
            colour=BASE_COLOR
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *query) -> None:
        """
        Plays current song.
        """
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice:
                await ctx.send('Connect first')
                return

            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        if query:
            if voice.is_playing():
                await self.queue(ctx)
                return

            if voice.is_paused():
                await voice.resume()
                return

            query = ' '.join(query)
            url, info = _yt.get_url(query)
            q.add(url, info['title'], ctx.author.mention)
            q.now_playing = len(q)

            stream = _yt.get_stream(url=url)
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream,
                                       before_options='-reconnect 1'
                                                      ' -reconnect_streamed 1'
                                                      ' -reconnect_delay_max 5')),
                after=lambda _: self._after(ctx, loop))
            await self.current(ctx)
        else:
            if voice.is_paused():
                voice.resume()

            if not q.is_empty:
                res = q.get_next()
                if not res:
                    await ctx.send('Queue ended')
                    return
            else:
                await ctx.send('No songs left')
                return

            stream = _yt.get_stream(url=res[0])
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream,
                                       before_options='-reconnect 1'
                                                      ' -reconnect_streamed 1'
                                                      ' -reconnect_delay_max 5')),
                after=lambda _: self._after(ctx, loop))
            await self.current(ctx)

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if q.play_next:
            ctx.message.content = ''
            return asyncio.run_coroutine_threadsafe(self.play(ctx), loop)

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context) -> None:
        """
        Displays current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        args = ctx.message.content.split(' ')[1:]
        if args:
            query = ' '.join(args)
            url, info = _yt.get_url(query)
            q.add(url, info['title'], ctx.author.mention)

            embed = discord.Embed(description=f'Queued: [{info["title"]}]({url})',
                                  color=BASE_COLOR)
            await ctx.send(embed=embed)
        else:
            desc = ''
            for index, item in enumerate(q.queue):
                url, title, mention = item
                desc += f'{index + 1}. [{title}]({url}) | {mention}\n'

            embed = discord.Embed(title='Current queue:',
                                  color=BASE_COLOR,
                                  description=desc)
            await ctx.send(embed=embed)

    @commands.command(aliases=['clr'])
    async def clear(self, ctx: commands.Context):
        """
        Clears current queue.
        """
        q = self._queues[ctx.guild.id]
        q.clear()

    @commands.command()
    async def loop(self, cxt: commands.Context, option: str = ''):
        """
        Changes loop option to None, Queue or Track
        """
        loop_setting = ['None', 'Current queue', 'Current track']

        q = self._queues[cxt.guild.id]
        if option:
            q._loop = ['None', 'Queue', 'Track'].index(option.capitalize())
        else:
            q._loop += 1
            if q._loop > 2:
                q._loop = 0

        embed = discord.Embed(description=f'Now looping is set to: `{loop_setting[q._loop]}`',
                              color=BASE_COLOR)
        await cxt.send(embed=embed)

    @commands.command(aliases=['rm'])
    async def remove(self, ctx: commands.Context, index: int):
        """
        Removes a song from queue by index.
        """
        q = self._queues[ctx.guild.id]
        res = q.remove(index - 1)

        embed = discord.Embed(
            description=f'Removed: [{res[1]}]({res[0]})',
            color=BASE_COLOR
        )
        await ctx.send(embed=embed)
