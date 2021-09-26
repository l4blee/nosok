import asyncio
import typing
from collections import defaultdict

import discord
from discord.ext import commands

import config.config as config
import exceptions
import utils
from base import BASE_COLOR, ERROR_COLOR
from bot import bot
from core import yt_handler as _yt
from utils import is_connected


class Queue:
    def __init__(self):
        self._tracks: list[tuple] = []
        self._loop: int = 0  # 0 - None; 1 - Current queue; 2 - Current track
        self.now_playing: int = 0
        self.play_next: bool = True

    def add(self, url: str, title: str, mention: discord.User.mention) -> None:
        self._tracks.append((url, title, mention))

    def get_next(self) -> typing.Optional[tuple]:
        self.now_playing += int(self._loop != 2)
        if self.now_playing >= len(self._tracks):
            if self._loop == 0:
                self.now_playing = 0
                self.play_next = False
                return None
            else:
                self.now_playing = 0

        ret = self._tracks[self.now_playing]

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
    def current(self) -> typing.Optional[tuple]:
        return self._tracks[self.now_playing] if len(self._tracks) > 0 else None

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: int):
        self._loop = value


class Music(commands.Cog):
    def __init__(self):
        self._queues: defaultdict[Queue] = defaultdict(Queue)
        self.bot = bot

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel = None) -> None:
        """
        Makes the bot join your current voice channel
        """
        if ctx.voice_client:
            await utils.send_embed(
                ctx=ctx,
                description='I am already connected to a voice channel!',
                color=ERROR_COLOR,
            )
            raise exceptions.AlreadyConnected

        voice = ctx.author.voice
        if not voice:
            await utils.send_embed(
                ctx=ctx,
                description='Connect to a voice channel first',
                color=ERROR_COLOR
            )
            raise exceptions.UserNotConnected

        if voice_channel:
            await voice_channel.connect()
        else:
            await voice.channel.connect()

    @commands.command(aliases=['s'])
    @commands.check(is_connected)
    async def stop(self, ctx: commands.Context) -> None:
        """
        Stops bot from playing current song.
        """
        q = self._queues[ctx.guild.id]
        q.play_next = False
        ctx.voice_client.stop()

    @commands.command(aliases=['l'])
    @commands.check(is_connected)
    async def leave(self, ctx: commands.Context) -> None:
        """
        Makes bot leave your current channel.
        """
        voice = ctx.voice_client
        if voice.is_playing():
            await self.stop(ctx)
        await voice.disconnect()

    @commands.command(aliases=['ps'])
    @commands.check(is_connected)
    async def pause(self, ctx: commands.Context) -> None:
        """
        Pauses current song. Use `play` command to resume.
        """
        voice = ctx.voice_client
        if voice.is_playing():
            voice.pause()
        else:
            await utils.send_embed(
                ctx=ctx,
                description='I am not playing yet!',
                color=ERROR_COLOR
            )

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
            raise exceptions.BotNotConnectedToChannel'''

    @commands.command(aliases=['c'])
    @commands.check(is_connected)
    async def current(self, ctx: commands.Context) -> None:
        """
        Displays current playing song.
        """
        voice = ctx.voice_client
        if not voice.is_playing():
            await utils.send_embed(
                ctx=ctx,
                description='I am not playing for now!',
                color=ERROR_COLOR
            )
            return

        q: Queue = self._queues[ctx.guild.id]
        current = q.current
        await utils.send_embed(
            ctx=ctx,
            title='Current song:',
            description=f'[{current[1]}]({current[0]}) | {current[2]}',
            color=BASE_COLOR
        )

    @commands.command(aliases=['n'])
    @commands.check(is_connected)
    async def next(self, ctx: commands.Context):
        ctx.voice_client.stop()

    @commands.command(aliases=['prev'])
    @commands.check(is_connected)
    async def previous(self, ctx: commands.Context):
        q = self._queues[ctx.guild.id]
        if len(q) > 0:
            q.now_playing -= 1
            if q.loop == 0 and q.now_playing < 0:
                print(q.loop, q.now_playing)
                q.now_playing = 0
                await ctx.send('No previous tracks')
                raise exceptions.NoPreviousTracks

            ctx.guild.voice_client.stop()
        else:
            await utils.send_embed(
                ctx=ctx,
                description='The queue is empty!',
                color=ERROR_COLOR
            )
            raise exceptions.QueueEmpty

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *query) -> None:
        """
        Plays current song.
        """
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice:
                await utils.send_embed(
                    ctx=ctx,
                    description='Connect to a voice channel first',
                    color=ERROR_COLOR
                )
                raise exceptions.UserNotConnected

            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        if query:
            if voice.is_playing():
                await self.queue(ctx, query)
                return

            if voice.is_paused():
                await voice.resume()
                await self.queue(ctx, query)
                return

            query = ' '.join(query)
            url, title = _yt.get_track(query)
            q.add(url, title, ctx.author.mention)
            q.now_playing = len(q) - 1

            stream = _yt.get_stream(url=url)
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream)),
                after=lambda _: self._after(ctx, loop))
            await self.current(ctx)
        else:
            if voice.is_paused():
                voice.resume()

            if not q.is_empty:
                res = q.get_next()
                if not res:
                    embed = discord.Embed(
                        description='The queue has ended',
                        color=BASE_COLOR
                    )
                    await ctx.send(embed=embed)
                    return
            else:
                embed = discord.Embed(
                    description='The are no songs in the queue',
                    color=ERROR_COLOR
                )
                await ctx.send(embed=embed)
                raise exceptions.QueueEmpty

            stream = _yt.get_stream(url=res[0])
            loop = asyncio.get_running_loop()
            voice.play(discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream)),
                after=lambda _: self._after(ctx, loop))
            await self.current(ctx)

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if q.play_next:
            ctx.message.content = ''
            return asyncio.run_coroutine_threadsafe(self.play(ctx), loop)

    async def _choose_track(self, ctx: commands.Context, tracks):
        def _check(reaction, user):
            return (
                reaction.emoji in config.OPTIONS.keys()
                and user == ctx.author
            )

        description = ''
        for index, track in enumerate(tracks):
            description += f"{index + 1}. [{track[1]}]({track[0]})\n\n"

        embed = discord.Embed(
            title='Choose one of these songs',
            description=description,
            color=BASE_COLOR
        )
        message = await ctx.send(embed=embed)

        for reaction in list(config.OPTIONS.keys())[:min(len(tracks), len(config.OPTIONS))]:
            await message.add_reaction(reaction)

        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=60, check=_check)
        except asyncio.TimeoutError:
            await message.delete()
            await ctx.message.delete()
            await ctx.send('Timeout has been exceeded')
            raise exceptions.TimeoutExceeded
        else:
            await message.delete()
            url, title = tracks[config.OPTIONS[reaction.emoji]]
            return url, title

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context, *query) -> None:
        """
        Displays current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        if query:
            url, title = _yt.get_track(query)
            q.add(url, title, ctx.author.mention)

            embed = discord.Embed(description=f'Queued: [{title}]({url})',
                                  color=BASE_COLOR)
            await ctx.send(embed=embed)
        else:
            if len(q) > 0:
                desc = ''
                for index, item in enumerate(q.queue):
                    url, title, mention = item
                    desc += f'{["", "Current ==> "][int(index == q.now_playing)]}' \
                            f'{index + 1}. [{title}]({url}) | {mention}\n'
            else:
                desc = 'There are no tracks in the queue for now!'

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

        embed = discord.Embed(description='Queue has been successfully cleared',
                              color=BASE_COLOR)
        await ctx.send(embed=embed)

    @commands.command()
    async def loop(self, cxt: commands.Context, option: str = ''):
        """
        Changes loop option to None, Queue or Track
        """
        loop_setting = ['None', 'Current queue', 'Current track']

        q = self._queues[cxt.guild.id]
        if option:
            q.loop = ['None', 'Queue', 'Track'].index(option.capitalize())
        else:
            q.loop += 1
            if q.loop > 2:
                q.loop = 0

        embed = discord.Embed(description=f'Now looping is set to: `{loop_setting[q.loop]}`',
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

    @commands.command()
    async def seek(self, ctx: commands.Context, index: int):
        """
        Seeks a specified track with an index and plays it
        """
        voice = ctx.guild.voice_client
        await self.stop()

        q = self._queues[ctx.guild.id]
        q.now_playing = index - 1

        while voice.is_playing():
            await asyncio.sleep(0.1)
        await self.play()

    @commands.command(aliases=['vol', 'v'])
    @commands.check(is_connected)
    async def volume(self, ctx: commands.Context, volume: float):
        if 0 > volume > 100:
            embed = discord.Embed(
                description=f'Volume must be in range `0` to `100`, not {volume}',
                color=ERROR_COLOR
            )
        else:
            voice = ctx.voice_client
            voice.volume = volume / 100
            embed = discord.Embed(
                description=f'Volume has been successfully changed to `{volume}%`'
            )
        await ctx.send(embed=embed)
