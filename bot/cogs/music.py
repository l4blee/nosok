import asyncio
from io import FileIO
from os import makedirs
from re import compile
from subprocess import DEVNULL
from typing import Generator, Optional

import discord
from discord import Embed
from discord.ext import commands

import exceptions
from base import BASE_COLOR, ERROR_COLOR
from core import music_handler, event_handler
from utils import (is_connected, send_embed,
                   get_components, run_blocking)

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s(" \
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
URL_REGEX = compile(URL_REGEX)

ITEM_SEPARATOR = ']]]]'

makedirs('bot/queues', exist_ok=True)


class Queue:
    __slots__ = ('_loop', 'now_playing', 'play_next', 'volume', 'guild_id', 'queue_file')

    def __init__(self, guild_id: int):
        self._loop: int = 0  # 0 - None; 1 - Current queue; 2 - Current track
        self.now_playing: int = -1
        self.play_next: bool = True
        self.volume: float = 1.0
        self.guild_id = guild_id

        self.queue_file = FileIO(f'bot/queues/{guild_id}.txt', 'a+')

    @property
    def tracks(self) -> list[tuple]:
        self.queue_file.seek(0)
        data = self.queue_file.read().decode('utf-8').split('\n')
        
        tracks = [tuple(i.split(ITEM_SEPARATOR)) for i in data if i]
        return tracks

    def _write_to_queue_file(self, items):
        to_write = [(ITEM_SEPARATOR.join(i) + '\n').encode('utf-8') for i in items]
        self.queue_file.writelines(to_write)

    def remove(self, index: int) -> tuple:
        tracks = self.tracks
        
        ret = tracks.pop(index)
        self.clear()
        self._write_to_queue_file(tracks)

        return ret

    def add(self, url: str, mention: discord.User.mention) -> None:
        self.queue_file.seek(0, 2)

        title = music_handler.get_info(url, is_url=True)[1]
        self._write_to_queue_file([url, title, mention])

    def get_next(self) -> Optional[tuple]:
        tracks = self.tracks

        self.now_playing += int(self._loop != 2)
        if self.now_playing >= len(tracks):
            if self._loop == 0:
                self.now_playing = -1
                self.play_next = False
                return None
            else:
                self.now_playing = 0
            
        return tracks[self.now_playing]

    def __len__(self):
        return len(self.tracks)

    def clear(self) -> None:
        self.queue_file.close()
        with open(f'bot/queues/{self.guild_id}.txt', 'w') as f:
            f.write('')

        self.queue_file = FileIO(f'bot/queues/{self.guild_id}.txt', 'a+')

    @property
    def is_empty(self) -> bool:
        return not bool(self.tracks)

    @property
    def queue(self) -> Generator:
        yield from self.tracks  # yields url, title, mention

    @property
    def current(self) -> Optional[tuple]:
        tracks = self.tracks
        return tracks[self.now_playing] if len(tracks) > 0 else None

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: int):
        if 0 > value > 2:
            raise ValueError('Loop value is out of range')

        self._loop = value


class Music(commands.Cog):
    __slots__ = ('_queues')

    def __init__(self):
        self._queues: dict = dict()

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel = None) -> None:
        """
        Makes the bot join your current voice channel
        """
        if ctx.voice_client:
            await send_embed(
                ctx=ctx,
                description='I am already connected to a voice channel!',
                color=ERROR_COLOR,
            )
            raise exceptions.AlreadyConnected

        voice = ctx.author.voice
        if not voice:
            await send_embed(
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
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = False
        ctx.voice_client.stop()
        while ctx.voice_client.is_playing():
            await asyncio.sleep(0.1)

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
        voice.cleanup()

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
            await send_embed(
                ctx=ctx,
                description='I am not playing yet!',
                color=ERROR_COLOR
            )

    @commands.command(aliases=['c'])
    @commands.check(is_connected)
    async def current(self, ctx: commands.Context) -> None:
        """
        Displays current playing song.
        """
        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        current = q.current

        if not voice.is_playing() or current is None:
            await send_embed(
                ctx=ctx,
                description='I am not playing any song for now!',
                color=ERROR_COLOR
            )
            return

        await send_embed(
            ctx=ctx,
            title='Current song:',
            description=f'[{current[1]}]({current[0]}) | {current[2]}',
            color=BASE_COLOR
        )

    @commands.command(aliases=['n', 'next'])
    @commands.check(is_connected)
    async def skip(self, ctx: commands.Context):
        """
        Skips the current track and plays the next one
        """
        if ctx.voice_client:
            ctx.voice_client.stop()

    @commands.command(aliases=['prev'])
    @commands.check(is_connected)
    async def previous(self, ctx: commands.Context):
        """
        Plays a track before the current one
        """
        q = self._queues[ctx.guild.id]
        res = await self._seek(ctx, q.now_playing)
        if res == -1:
            await send_embed(
                ctx=ctx,
                description='There are no tracks before current song',
                color=ERROR_COLOR
            )
            raise exceptions.NoTracksBefore

    @staticmethod
    async def get_pagination(ctx: commands.Context, *tracks):
        embeds = []
        tracks = tracks[0]

        for url, title, thumbnail in tracks:
            embed = Embed(title=title, url=url)
            embed.set_thumbnail(url=thumbnail)
            embed.set_author(name=ctx.author)
            embeds.append(embed)

        current = 0
        message = await ctx.reply(
            '**Choose one of the following tracks:**',
            embed=embeds[current],
            components=get_components(embeds, current)
        )

        while True:
            try:
                interaction = await ctx.bot.wait_for(
                    'button_click',
                    check=lambda i: i.component.id in ['back', 'forward', 'lock'],
                    timeout=20.0
                )

                if interaction.component.id == 'back':
                    current -= 1
                elif interaction.component.id == 'forward':
                    current += 1
                elif interaction.component.id == 'lock':
                    if (track := tracks[current]) is not None:
                        await message.delete()
                        return track

                if current == len(embeds):
                    current = 0
                elif current < 0:
                    current = len(embeds) - 1

                await message.edit(
                    '**Choose one of the following tracks:**',
                    embed=embeds[current],
                    components=get_components(embeds, current)
                )

                # Doesn't apply changes if I don't use both methods idk why
                await interaction.respond(
                    type=6, 
                    embed=embeds[current],
                    components=get_components(embeds, current)
                )
            except asyncio.TimeoutError:
                await message.delete()
                break

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *query) -> None:
        """
        Plays current song.
        """
        query = ' '.join(query)
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice:
                await send_embed(
                    ctx=ctx,
                    description='Connect to a voice channel first',
                    color=ERROR_COLOR
                )
                raise exceptions.UserNotConnected

            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        if query != '':
            if voice.is_playing():
                await self.queue(ctx, query)
                return

            if voice.is_paused():
                await voice.resume()
                await self.queue(ctx, query)
                return

            url = query if URL_REGEX.match(query) else music_handler.get_url(query)

            q.add(url, ctx.author.mention)
            q.now_playing = len(q) - 1
            stream = music_handler.get_stream(url)
            loop = ctx.bot.loop
            await self._play(ctx, stream, loop)
        else:
            if voice.is_paused():
                voice.resume()
                return

            if not q.is_empty:
                res = q.get_next()
                if not res:
                    await send_embed(
                        ctx=ctx,
                        description='The queue has ended',
                        color=BASE_COLOR
                    )
                    event_handler.on_song_end(ctx)
                    return
            else:
                await send_embed(
                    ctx=ctx,
                    description='There are no songs in the queue',
                    color=ERROR_COLOR
                )
                event_handler.on_song_end(ctx)
                raise exceptions.QueueEmpty

            stream = music_handler.get_stream(res[0])
            loop = ctx.bot.loop
            await self._play(ctx, stream, loop)

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if q.play_next:
            ctx.message.content = ''
            return asyncio.run_coroutine_threadsafe(self.play(ctx), loop)
        else:
            event_handler.on_song_end(ctx)

    async def _play(self, ctx: commands.Context, stream, loop):
        q = self._queues[ctx.guild.id]
        voice = ctx.voice_client
        audio_source = discord.FFmpegPCMAudio(stream,
                                              stderr=DEVNULL,
                                              before_options='-reconnect 1'
                                                             ' -reconnect_streamed 1'
                                                             ' -reconnect_delay_max 5')
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)
        voice.play(audio_source, after=lambda _: self._after(ctx, loop))

        event_handler.on_song_start(ctx)

        await self.current(ctx)

    async def _get_track(self, ctx: commands.Context, query: str) -> tuple:
        if URL_REGEX.match(query):
            song = music_handler.get_info(query, is_url=True)
        else:
            tracks = list(await run_blocking(music_handler.get_infos, ctx.bot, query=query))
            song = await self._choose_track(ctx, tracks)

        return song

    async def _choose_track(self, ctx: commands.Context, tracks):
        track = await self.get_pagination(ctx, tracks)

        if not track:
            return

        url, title, _ = track
        return url, title

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context, *query) -> None:
        """
        Displays current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        query = ' '.join(query)
        if query:
            song = await self._get_track(ctx, query)
            
            if not song:
                await send_embed(
                    ctx=ctx,
                    description='No tracks were specified',
                    color=BASE_COLOR)
                
                raise exceptions.NoTracksSpecified

            if song is None:
                await send_embed(
                    ctx=ctx,
                    description='Canceled.',
                    color=BASE_COLOR)
                return
            
            url, title = song

            q.add(url, ctx.author.mention)
            await send_embed(
                ctx=ctx,
                description=f'Queued: [{title}]({url})',
                color=BASE_COLOR
            )
        else:
            if len(q) > 0:
                desc = ''
                for index, item in enumerate(q.queue):
                    url, title, mention = item
                    desc += f'{["", "now -> "][int(index == q.now_playing)]}' \
                            f'{index + 1}.\t[{title}]({url}) | {mention}\n'
            else:
                desc = 'There are no tracks in the queue for now!'

            await send_embed(
                ctx=ctx,
                title='Current queue:',
                color=BASE_COLOR,
                description=desc
            )

    @commands.command(aliases=['clr'])
    async def clear(self, ctx: commands.Context):
        """
        Clears current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        q.clear()

        await send_embed(
            ctx=ctx,
            description='Queue has been successfully cleared',
            color=BASE_COLOR
        )

    @commands.command()
    async def loop(self, ctx: commands.Context, option: str = ''):
        """
        Changes loop option to None, Queue or Track
        """
        loop_setting = ['None', 'Current queue', 'Current track']

        q: Queue = self._queues[ctx.guild.id]
        if option:
            q.loop = ['None', 'Queue', 'Track'].index(option.capitalize())
        else:
            q.loop += 1
            if q.loop > 2:
                q.loop = 0

        await send_embed(ctx=ctx, 
                         description=f'Now looping is set to: `{loop_setting[q.loop]}`',
                         color=BASE_COLOR)

    @commands.command(aliases=['rm'])
    async def remove(self, ctx: commands.Context, index: int):
        """
        Removes a song from the queue by its index.
        """
        q: Queue = self._queues[ctx.guild.id]
        try:
            res = q.remove(index - 1)
        except IndexError:
            await send_embed(
                ctx=ctx,
                description='No specified track in the queue.',
                color=ERROR_COLOR
            )
            return

        url, _ = res
        title = music_handler.get_info(url, is_url=True)[1]

        await send_embed(
            ctx=ctx,
            description=f'Removed: [{title}]({url})',
            color=BASE_COLOR
        )

    async def _seek(self, ctx: commands.Context, index: int):
        q: Queue = self._queues[ctx.guild.id]
        if 1 <= index <= len(q):
            q.now_playing = index - 2
            await self.skip(ctx)
        elif q.is_empty:
            await send_embed(
                ctx=ctx,
                description='Queue is empty!',
                color=ERROR_COLOR
            )
            raise exceptions.QueueEmpty
        else:
            return -1

    @commands.command()
    async def seek(self, ctx: commands.Context, index: int):
        """
        Seeks a specified track with an index and plays it.
        """
        q = self._queues[ctx.guild.id]
        res = await self._seek(ctx, index)
        if res == -1:
            await send_embed(
                ctx=ctx,
                description=f'Index must be in range `1` to `{len(q)}`, not `{index}`',
                color=ERROR_COLOR
            )
            raise IndexError('Index out of range')
        else:
            await self.play(ctx)

    @commands.command(aliases=['vol', 'v'])
    @commands.check(is_connected)
    async def volume(self, ctx: commands.Context, volume: float):
        """
        Adjusts the volume.
        """
        if 0 > volume > 100:
            await send_embed(
                ctx=ctx,
                description=f'Volume must be in the range from `0` to `100`, not {volume}',
                color=ERROR_COLOR
            )
        else:
            ctx.voice_client.source.volume = volume / 100
            self._queues[ctx.guild.id].volume = volume / 100
            await send_embed(
                ctx=ctx,
                description=f'Volume has been successfully changed to `{volume}%`',
                color=BASE_COLOR
            )

    @commands.command(aliases=['sch'])
    async def search(self, ctx: commands.Context, *query):
        """
        Searches for a song on YouTube and gives you 5 options to choose.
        """
        q: Queue = self._queues[ctx.guild.id]
        query = ' '.join(query)

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client

        tracks = list(await run_blocking(music_handler.get_infos, ctx.bot, query=query))
        track = await self._choose_track(ctx, tracks)

        if not track:
            await send_embed(
                ctx=ctx,
                description='No tracks were specified',
                color=BASE_COLOR)
            raise exceptions.NoTracksSpecified
        
        url, title = track

        q.add(url, ctx.author.mention)
        if not voice.is_playing():
            stream = music_handler.get_stream(url)
            loop = ctx.bot.loop
            await self._play(ctx, stream, loop)
        else:
            await send_embed(
                ctx=ctx,
                description=f'Queued: [{title}]({url})',
                color=BASE_COLOR
            )
