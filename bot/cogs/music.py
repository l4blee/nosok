import asyncio
import pickle
from os import makedirs, getenv
from re import compile
from subprocess import DEVNULL
from typing import Optional, Union
from enum import Enum
from dataclasses import dataclass

import discord
from discord import Embed
from discord.ext import commands

import exceptions
from database import db
from languages import get_phrase
from player import BassVolumeTransformer
from base import BASE_COLOR, ERROR_COLOR
from core import music_handler, event_handler
from utils import is_connected, send_embed, get_components

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s(" \
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
URL_REGEX = compile(URL_REGEX)

makedirs('bot/queues', exist_ok=True)


class Looping(Enum):
    NONE, CURRENT_QUEUE, CURRENT_TRACK = range(3)


@dataclass()
class Track:
    url: str
    title: str
    mention: str

    def to_list(self) -> tuple:
        return self.url, self.title, self.mention

    @classmethod
    def from_list(self, data: Union[list, tuple]):
        return Track(*data)


class Queue:
    __slots__ = ('_loop', 'now_playing', 'play_next', '_volume',
                 'queue_file', '_bass')

    def __init__(self, guild_id: int):
        self._loop: Looping = Looping.NONE
        self.now_playing: int = -1
        self.play_next: bool = True

        self._volume: float = 1.0
        self._bass: float = 0.0

        self.queue_file = f'bot/queues/{guild_id}'
        self.clear()

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = max(min(value, 2.0),0.0)

    @property
    def bass_accentuate(self) -> float:
        return self._bass

    @bass_accentuate.setter
    def bass_accentuate(self, value: float):
        self._bass = min(max(value, -20), 200)

    @property
    def tracks(self) -> list[Track]:
        with open(self.queue_file, 'rb') as f:
            return pickle.load(f, encoding='utf-8')

    def _write_to_queue(self, data: list) -> None:
        # First we get the alredy-saved queue
        with open(self.queue_file, 'rb') as f:
            previous = pickle.load(f)

        # Then concat and dump back again
        with open(self.queue_file, 'wb') as f:
            pickle.dump(previous + data, f, protocol=-1)

    def remove(self, index: int) -> Track:
        tracks = self.tracks

        ret = tracks.pop(index)
        self.clear()
        self._write_to_queue(tracks)

        return ret

    async def add(self, url: str, mention: discord.User.mention, title: str = None) -> None:
        title = title or (await music_handler.get_metadata(url, is_url=True)).title

        self._write_to_queue([Track(url, title, mention)])

    def get_next(self) -> Optional[Track]:
        tracks = self.tracks

        self.now_playing += int(self._loop is not Looping.CURRENT_TRACK)
        if self.now_playing >= len(tracks):
            if self._loop is Looping.NONE:
                self.now_playing = -1
                self.play_next = False
                return None
            else:
                self.now_playing = 0

        return tracks[self.now_playing]

    def __len__(self) -> int:
        return len(self.tracks)

    def clear(self) -> None:
        with open(self.queue_file, 'wb') as f:
            pickle.dump([], f)

    @property
    def is_empty(self) -> bool:
        return not bool(self.tracks)

    @property
    def current(self) -> Optional[Track]:
        tracks = self.tracks
        return tracks[self.now_playing] if len(tracks) > 0 else None

    @property
    def loop(self) -> int:
        return self._loop.value

    @loop.setter
    def loop(self, value: int):
        value = value if value >= 0 and value <= 2 else 0
        self._loop = Looping(value)


class Music(commands.Cog):
    __slots__ = ('_queues', '_bot')

    def __init__(self, bot):
        self._queues: dict = dict()
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self._queues = {g.id: Queue(g.id) for g in self._bot.guilds}

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context, voice_channel: discord.VoiceChannel = None) -> None:
        """
        Makes the bot join your current voice channel
        """
        if ctx.voice_client:
            raise exceptions.AlreadyConnected

        if voice_channel:
            await voice_channel.connect()
            return

        if not (voice := ctx.author.voice):
            raise exceptions.UserNotConnected

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
        Makes bot leave voice channel.
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
        Pauses current song.
        """
        voice = ctx.voice_client
        if voice.is_playing():
            voice.pause()
        else:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'not_playing'),
                color=ERROR_COLOR
            )

    @commands.command(aliases=['cur'])
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
                description=await get_phrase(ctx, 'not_playing'),
                color=ERROR_COLOR
            )
            return

        await send_embed(
            ctx=ctx,
            title=await get_phrase(ctx, 'current'),
            description=f'[{current.title}]({current.url}) | {current.mention}',
            color=BASE_COLOR
        )

    @commands.command(aliases=['n', 'next'])
    @commands.check(is_connected)
    async def skip(self, ctx: commands.Context):
        """
        Skips the current track and plays the next one.
        """
        if ctx.voice_client:
            ctx.voice_client.stop()  # Triggers _after and plays again

    @commands.command(aliases=['prev'])
    @commands.check(is_connected)
    async def previous(self, ctx: commands.Context):
        """
        Plays a track before the current one.
        """
        q = self._queues[ctx.guild.id]
        # As now_playing is set from 0 index
        res = await self._seek(ctx, q.now_playing)
        if not res:
            raise exceptions.NoTracksBefore

    @staticmethod
    async def get_track_pagination(ctx: commands.Context, *tracks: list[Track]):
        embeds = []

        for item in tracks:
            embed = Embed(title=item.title, url=item.url, color=BASE_COLOR)
            embed.set_thumbnail(url=item.thumbnail)
            embed.set_author(name=ctx.author)
            embeds.append(embed)

        search_view = get_components('search')
        view = search_view(
            embeds=embeds,
            timeout=15
        )

        message = await ctx.send(
            f'**{await get_phrase(ctx, "choose_track")}**',
            embed=embeds[0],
            view=view
        )

        await view.wait()
        success = not await message.delete()
        return tracks[view.current] if success else None

    @commands.command(aliases=['p', 'р', 'п'])
    async def play(self, ctx: commands.Context, *, query: str = None) -> None:
        """
        Plays specified track or resumes current song.
        """
        voice = ctx.voice_client
        if not voice:
            if not ctx.author.voice or not ctx.author.voice.channel:
                raise exceptions.UserNotConnected

            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        if query:
            if len(query) < int(getenv('MINIMAL_QUEURY_LENGTH', 10)):
                raise exceptions.QueryTooShort
            if voice.is_playing():
                await self.queue(ctx, query=query)
                return

            if voice.is_paused():
                await voice.resume()
                await self.queue(ctx, query=query)
                return

            url = query if URL_REGEX.match(query) else await music_handler.get_url(query)

            await q.add(url, ctx.author.mention)
            q.now_playing = len(q) - 1
        else:
            if voice.is_paused():
                voice.resume()
                return

            if not q.is_empty:
                res = q.get_next()
                if not res:
                    await send_embed(
                        ctx=ctx,
                        description=await get_phrase(ctx, 'queue_ended'),
                        color=BASE_COLOR)
                    event_handler.on_song_end(ctx)
                    return

                url = res.url
            else:
                event_handler.on_song_end(ctx)
                await send_embed(
                    ctx=ctx,
                    description=await get_phrase(ctx, 'queue_empty'),
                    color=ERROR_COLOR
                )
                return

        stream = await music_handler.get_stream(url)
        loop = ctx.bot.loop
        await self._play(ctx, stream, loop)

    def _after(self, ctx: commands.Context, loop: asyncio.AbstractEventLoop):
        q: Queue = self._queues[ctx.guild.id]
        if q.play_next:
            return asyncio.run_coroutine_threadsafe(self.play(ctx), loop)

        event_handler.on_song_end(ctx)

    async def _play(self, ctx: commands.Context, stream, loop):
        q = self._queues[ctx.guild.id]
        voice = ctx.voice_client
        audio_source = discord.FFmpegPCMAudio(stream,
                                              stderr=DEVNULL,
                                              before_options='-reconnect 1'
                                                             ' -reconnect_streamed 1'
                                                             ' -reconnect_delay_max 5')
        audio_source = BassVolumeTransformer(
            audio_source, volume=q.volume, bass_accentuate=q.bass_accentuate)

        voice.play(audio_source, after=lambda _: self._after(ctx, loop))

        event_handler.on_song_start(ctx)

        await self.current(ctx)

    async def _get_track(self, ctx: commands.Context, query: str) -> Track:
        if URL_REGEX.match(query):
            song = await music_handler.get_metadata(query, is_url=True)
        else:
            tracks = await music_handler.get_metas(query)
            song = await self.get_track_pagination(ctx, *tracks)

        return song

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context, *, query: str = None) -> None:
        """
        Displays current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        if query:
            if len(query) < int(getenv('MINIMAL_QUEURY_LENGTH', 10)):
                raise exceptions.QueryTooShort()
            song = await self._get_track(ctx, query)

            if not song:
                raise exceptions.NoTracksSpecified

            if song is None:
                await send_embed(
                    ctx=ctx,
                    description=await get_phrase(ctx, 'cancelled'),
                    color=BASE_COLOR)
                return

            await q.add(
                url=song.url,
                title=song.title,
                mention=ctx.author.mention
            )
            await send_embed(
                ctx=ctx,
                description=f'{await get_phrase(ctx, "queued")} [{song.title}]({song.url})',
                color=BASE_COLOR
            )
        else:
            tracks = list(q.tracks)
            now_alias = await get_phrase(ctx, 'now') + ' -> '
            if len(tracks) > 0:
                desc = ''
                for index, item in enumerate(tracks):
                    desc += f'{["", now_alias][int(index == q.now_playing)]}' \
                            f'{index + 1}.\t[{item.title}]({item.url}) | {item.mention}\n'
            else:
                desc = await get_phrase(ctx, 'queue_empty')

            await send_embed(
                ctx=ctx,
                title=await get_phrase(ctx, 'queue'),
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
            description=await get_phrase(ctx, 'queue_cleared'),
            color=BASE_COLOR
        )

    @commands.command()
    async def loop(self, ctx: commands.Context, option: str = None):
        """
        Changes loop option to None, Queue or Track.
        """
        loop_setting = ['None', 'Current queue', 'Current track']

        q: Queue = self._queues[ctx.guild.id]
        if option is not None:
            q.loop = ['none', 'queue', 'track'].index(option.lower())
        else:
            q.loop += 1

        await send_embed(ctx=ctx,
                         description=f'{await get_phrase(ctx, "looping_set")} `{loop_setting[q.loop]}`',
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
                description=await get_phrase(ctx, 'remove_error'),
                color=ERROR_COLOR
            )
            return

        await send_embed(
            ctx=ctx,
            description=f'{await get_phrase(ctx, "removed")}: [{res.title}]({res.url})',
            color=BASE_COLOR
        )

    async def _seek(self, ctx: commands.Context, index: int) -> bool:
        # Seeks with index given as if we counted from 1
        q: Queue = self._queues[ctx.guild.id]
        q.play_next = True

        if q.is_empty:
            raise exceptions.QueueEmpty
        elif 1 <= index <= len(q):
            q.now_playing = index - 2
            # Shifting it 2 back as now_playing counts from 0
            # and get_next method in play gonna move it 1 step further
            await self.skip(ctx)
            return True
        return False

    @commands.command()
    async def seek(self, ctx: commands.Context, index: int):
        """
        Seeks a specified track with an index and plays it.
        """
        q = self._queues[ctx.guild.id]

        res = await self._seek(ctx, index)
        if not res:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'seek_error') % dict(max_index=len(q), index=index),
                color=ERROR_COLOR
            )
            return

        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            await self.play(ctx)

    @commands.command(aliases=['vol', 'v'])
    @commands.check(is_connected)
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Adjusts the volume.
        """
        q: Queue = self._queues[ctx.guild.id]
        if 0 > float(volume) > 100:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'volume_error') % dict(volume=volume),
                color=ERROR_COLOR
            )
            return

        q.volume = volume / 100
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.source.volume = volume / 100

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'volume_set') % dict(volume=q.volume * 100),
            color=BASE_COLOR
        )

    @commands.command(aliases=['sch'])
    async def search(self, ctx: commands.Context, *, query: str):
        """
        Searches for a song and gives you 5 options to choose.
        """
        q: Queue = self._queues[ctx.guild.id]

        if len(query) < int(getenv('MINIMAL_QUEURY_LENGTH', 10)):
            raise exceptions.QueryTooShort

        tracks = await music_handler.get_metas(query)
        track = await self.get_track_pagination(ctx, *tracks)

        if track is None:
            raise exceptions.NoTracksSpecified

        await q.add(
            url=track.url,
            title=track.title,
            mention=ctx.author.mention
        )

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        voice = ctx.voice_client

        if not voice.is_playing():
            stream = await music_handler.get_stream(track.url)
            loop = ctx.bot.loop
            await self._play(ctx, stream, loop)
        else:
            await send_embed(
                ctx=ctx,
                description=f'{await get_phrase(ctx, "queued")} [{track.title}]({track.url})',
                color=BASE_COLOR
            )

    @commands.command(aliases=['bb'])
    @commands.check(is_connected)
    async def bass_boost(self, ctx: commands.Context, level: float):
        """
        Boosts a bass line for the track.
        """
        q: Queue = self._queues[ctx.guild.id]

        q.bass_accentuate = level
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.source.bass_accentuate = level

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'bass_boost_set') % dict(level=q.bass_accentuate),
            color=BASE_COLOR
        )

    # Playlists

    @commands.group(aliases=['plists', 'playlist', 'pl'])
    async def playlists(self, ctx: commands.Context):
        """
        Playlists-realated category.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help('playlists')
            return

    @playlists.command(name='show')
    async def show_playlist(self, ctx: commands.Context, *, name: str):
        """
        Displays an existing playlist for this guild with given name.
        """
        record = db.guilds.playlists.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )

        if record is None:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'playlist_doesnt_exist') % dict(name=name),
                color=ERROR_COLOR)
            return

        playlist = [Track.from_list(i) for i in record.get('playlist')]
        description = ''
        for index, item in enumerate(playlist):
            description += f'{index + 1}.\t[{item.title}]({item.url}) | {item.mention}\n'

        embed = Embed(
            title=f'{name} (share code: {ctx.guild.id}-{"_".join(name.split(" "))}):',
            description=description,
            color=BASE_COLOR
        )

        playlist_view = get_components('playlist')
        view = playlist_view(self, timeout=10)

        message = await ctx.send(
            embed=embed,
            view=view
        )

        await view.wait()
        await message.edit(view=view)

        if (callback := view.returned_callback) is not None:
            await callback(ctx, name=name)

    async def rename_playlist(self, ctx, name):
        entry = await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_choose_name') % dict(name=name),
            color=BASE_COLOR
        )

        try:
            msg = await ctx.bot.wait_for(
                'message',
                timeout=15
            )

            db.guilds.playlists.update_one(
                {
                    'name': name,
                    'guild_id': ctx.guild.id
                },
                {
                    '$set': {
                        'name': msg.content
                    }
                }
            )
        except asyncio.TimeoutError:
            await entry.delete()
            return

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_name_change') % dict(old_name=name, new_name=msg.content),
            color=BASE_COLOR
        )

    @playlists.command(name='create', aliases=['c'])
    async def create_playlist(self, ctx: commands.Context, *, name: str):
        """
        Creates/changes a playlist from current queue.
        """
        q: Queue = self._queues[ctx.guild.id]
        if q.is_empty:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'queue_empty'),
                color=ERROR_COLOR)
            return

        db.guilds.playlists.update_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            },
            {
                '$set': {
                    'playlist': [i.to_list() for i in q.tracks]
                }
            },
            upsert=True
        )

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_created') % dict(name=name),
            color=BASE_COLOR)

    @playlists.command(name='load', aliases=['l'])
    async def load_playlist(self, ctx: commands.Context, *, name: str):
        """
        Loads and existing playlist.
        """
        q: Queue = self._queues[ctx.guild.id]

        record = db.guilds.playlists.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )

        if record is None:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'playlist_doesnt_exist') % dict(name=name),
                color=ERROR_COLOR
            )
            return

        playlist = [Track.from_list(i) for i in record.get('playlist')]

        q.clear()
        for i in playlist:
            await q.add(
                url=i.url,
                title=i.title,
                mention=i.mention
            )

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_loaded') % dict(name=name),
            color=BASE_COLOR)

        await self.play(ctx)

    @playlists.command(name='delete', aliases=['rm', 'remove', 'del'])
    async def delete_playlist(self, ctx: commands.Context, *, name: str):
        """
        Deletes a playlist with the name given.
        """
        result = db.guilds.playlists.delete_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if result.deleted_count == 0:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'playlist_doesnt_exist') % dict(name=name),
                color=ERROR_COLOR)
            return

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_deleted') % dict(name=name),
            color=BASE_COLOR
        )

    @playlists.command(name='list', aliases=['li', 'ls'])
    async def list_playlists(self, ctx: commands.Context):
        """
        Displays all playlists from the current guild or the one mentioned.
        """
        record = db.guilds.playlists.find(
            {'guild_id': ctx.guild.id}
        )

        if record.explain()['executionStats']['nReturned'] > 0:
            names = [
                f'**{index + 1}.** {item.get("name")}' for index, item in enumerate(record)]
            description = '\n'.join(names)
        else:
            description = await get_phrase(ctx, 'no_playlists')

        await send_embed(
            ctx=ctx,
            title=await get_phrase(ctx, 'playlists_available'),
            description=description,
            color=BASE_COLOR
        )

    @playlists.command(aliases=['as'])
    async def add_shared(self, ctx: commands.Context, share_code: str):
        """
        Adds an existing playlist from another guild.
        """
        guild_id, name = share_code.split('-')
        name = ' '.join(name.split('_'))
        record = db.guilds.playlists.find_one(
            {
                'guild_id': int(guild_id),
                'name': name
            }
        )
        if record is None:
            await send_embed(
                ctx=ctx,
                description=await get_phrase(ctx, 'playlist_doesnt_exist') % dict(name=name),
                color=ERROR_COLOR)
            return

        db.guilds.playlists.replace_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            },
            {
                'guild_id': ctx.guild.id,
                'name': name,
                'playlist': record.get('playlist')
            },
            upsert=True
        )

        await send_embed(
            ctx=ctx,
            description=await get_phrase(ctx, 'playlist_shared') % dict(name=name),
            color=BASE_COLOR
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
