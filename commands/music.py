from typing import Union
from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos
import discord
from collections import defaultdict
import asyncio
from commands import utils
from urllib.parse import urlparse
from subprocess import DEVNULL

WAIT_UNTIL_DELETE = float(5)


class QueueElement:
    def __init__(self, title: str, url: str, added_by: discord.Member.mention):
        self.title = title
        self.url = url
        self.added_by = added_by

    def __repr__(self):
        return str(self.title)


class SongQueue:
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
        if index < len(self.__queue):
            del self.__queue[index]

    def __next__(self):
        if not self.__queue:
            return None

        self.now_playing += 1
        if self.now_playing >= len(self.__queue):
            self.now_playing = -1
            if not self.repeat:
                return str()

        return self.__queue[self.now_playing]

    def __getitem__(self, item):
        return self.__queue[item]

    def __repr__(self):
        return ' '.join(str(i) for i in self.__queue)

    def __len__(self):
        return len(self.__queue)


class MusicClient:
    __queues = defaultdict(SongQueue)

    ytdl_opts = {
        'format': 'bestaudio/best',
        'quiet': True
    }

    def __init__(self, client):
        self.__client = client

    async def main(self, args: tuple, msg: discord.Message, command: str):
        await eval(f'self.{command}(args, msg)')

    @staticmethod
    def get_voice_instance(guild_id: discord.Guild.id, client: discord.client):
        for voice_client in client.voice_clients:
            if voice_client.guild.id == guild_id:
                return voice_client
        else:
            return None

    async def create_ytdl_source(self, source_url: str):
        url = YoutubeDL(self.ytdl_opts).extract_info(source_url, download=False)['formats'][0]['url']
        return discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            url, stderr=DEVNULL,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        )

    async def now_playing(self, channel: discord.TextChannel, song: QueueElement):
        info = YoutubeDL(self.ytdl_opts).extract_info(song.url, download=False)
        return await channel.send(
            embed=utils.create_embed(f'[{info["title"]}]({song.url})', 'Now playing:', info['thumbnails'][0]['url'])
        )

    async def search(self, args: tuple, msg: discord.Message, return_to_user=True):
        if urlparse(args[0]).scheme != '':
            return args[0]

        search = SearchVideos(' '.join(args), max_results=5, mode='dict')
        links = [i['link'] for i in search.result()['search_result']]

        if return_to_user:
            await msg.channel.send(embed=utils.create_embed('\n'.join(links)), delete_after=WAIT_UNTIL_DELETE)

        return links[0]

    async def join(self, args: tuple, msg: discord.Message):
        voice = msg.author.voice
        if voice:
            voice_clients = [i.guild.id for i in self.__client.voice_clients]
            if msg.guild.id in voice_clients:
                await msg.channel.send(
                    embed=utils.create_embed('I am already connected to a voice channel!'),
                    delete_after=WAIT_UNTIL_DELETE
                )
            else:
                await voice.channel.connect()
        else:
            await msg.channel.send(
                embed=utils.create_embed('Connect to a voice channel first'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def leave(self, args: tuple, msg: Union[discord.Message, discord.Member]):
        instance = self.get_voice_instance(msg.guild.id, self.__client)
        if instance:
            await instance.disconnect()
        else:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet!'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def play(self, args: tuple, msg: discord.Message, repeat=True, skipped=True):
        instance = self.get_voice_instance(msg.guild.id, self.__client)

        if instance:
            this_queue = self.__queues[msg.guild.id]

            if not this_queue and not args:
                await msg.channel.send(
                    embed=utils.create_embed('Please specify a url/title of a track you want to play'),
                    delete_after=WAIT_UNTIL_DELETE
                )
                return -1

            instance = self.get_voice_instance(msg.guild.id, self.__client)
            if args:
                url = await self.search(args, msg, return_to_user=False)
                info = YoutubeDL(self.ytdl_opts).extract_info(url, download=False)
                this_queue.add_song(info['title'], url, msg.author.mention)

                if instance.is_playing():
                    await msg.channel.send(
                        embed=utils.create_embed(f'Queued [{info["title"]}]({url})'),
                        delete_after=WAIT_UNTIL_DELETE
                    )

                if not instance.is_playing():
                    this_queue.now_playing = len(this_queue) - 2

            if not instance.is_playing() and not instance.is_paused():
                song = next(this_queue)
                if not isinstance(song, QueueElement):
                    if song is None:
                        await msg.channel.send(
                            embed=utils.create_embed('Queue is empty, add something'),
                            delete_after=WAIT_UNTIL_DELETE)
                        return -1
                    elif isinstance(song, str):
                        prefix = utils.get_prefix(msg)
                        await msg.channel.send(
                            embed=utils.create_embed(f'Use command `{prefix}repeat` to enable queue repeating'),
                            delete_after=WAIT_UNTIL_DELETE
                        )
                        return -1

                loop = asyncio.get_running_loop()
                source = await self.create_ytdl_source(song.url)
                notification = await self.now_playing(msg.channel, song)
                instance.play(source, after=lambda e: self.__after(tuple(), msg, loop, notification))

                if skipped:
                    this_queue.play_after = True

            elif instance.is_paused():
                prefix = utils.get_prefix(msg)
                await msg.channel.send(
                    embed=utils.create_embed(f'Current track is paused, type `{prefix}resume` or `{prefix}stop`'),
                    delete_after=WAIT_UNTIL_DELETE
                )

        elif repeat:
            await self.join(tuple(), msg)
            await self.play(args, msg, repeat=False)

    def __after(self, argv: tuple, msg: discord.Message, loop: asyncio.AbstractEventLoop,
                notification: discord.Message):
        queue = self.__queues[msg.guild.id]
        if queue.play_after:
            asyncio.run_coroutine_threadsafe(self.play(argv, msg), loop)
        asyncio.run_coroutine_threadsafe(notification.delete(), loop)

    async def queue(self, args: tuple, msg: discord.Message):
        if args:
            url = await self.search(args, msg, return_to_user=False)
            info = YoutubeDL(self.ytdl_opts).extract_info(url, download=False)
            self.__queues[msg.guild.id].add_song(info['title'], url, msg.author.mention)

            await msg.channel.send(
                embed=utils.create_embed(f'Queued [{info["title"]}]({url})'),
                delete_after=WAIT_UNTIL_DELETE
            )
        else:
            desc = '\n'.join([f'[{song.title}]({song.url}) [{song.added_by}]' for song in self.__queues[msg.guild.id]])

            await msg.channel.send(
                embed=utils.create_embed(desc, title='Current playlist:'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def stop(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg.guild.id, self.__client)
        queue = self.__queues[msg.guild.id]
        queue.play_after = False

        if instance:
            instance.stop()
            await asyncio.sleep(0.5)
            queue.play_after = True
            queue.now_playing = -1
        else:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def pause(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg.guild.id, self.__client)

        if instance:
            if instance.is_paused():
                await msg.channel.send(
                    embed=utils.create_embed('Audio is already paused'),
                    delete_after=WAIT_UNTIL_DELETE
                )
            else:
                instance.pause()
        else:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def resume(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg.guild.id, self.__client)

        if instance:
            if instance.is_playing():
                await msg.channel.send(
                    embed=utils.create_embed('Audio is already playing'),
                    delete_after=WAIT_UNTIL_DELETE
                )
            else:
                instance.resume()
        else:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet'),
                delete_after=WAIT_UNTIL_DELETE
            )

    async def clear(self, args: tuple, msg: discord.Message):
        queue = self.__queues[msg.guild.id]
        for _ in range(len(queue)):
            queue.remove_song(0)

        await msg.channel.send(
            embed=utils.create_embed('Queue has been successfully cleared'),
            delete_after=WAIT_UNTIL_DELETE
        )

    async def repeat(self, args: tuple, msg: discord.Message):
        queue = self.__queues[msg.guild.id]
        queue.repeat = not queue.repeat

        await msg.channel.send(
            embed=utils.create_embed('Queue repeating has been successfully ' + ['disabled', 'enabled'][queue.repeat]),
            delete_after=WAIT_UNTIL_DELETE
        )

    async def skip(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg.guild.id, self.__client)

        if not instance:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet'),
                delete_after=WAIT_UNTIL_DELETE
            )
            return -1

        if instance.is_playing():
            instance.stop()
            self.__queues[msg.guild.id].play_after = False
            await asyncio.sleep(0.5)
            await self.play(tuple(), msg, skipped=True)

    async def volume(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg.guild.id, self.__client)

        if not instance:
            await msg.channel.send(
                embed=utils.create_embed('I am not connected to a voice channel yet'),
                delete_after=WAIT_UNTIL_DELETE
            )
            return -1

        new_volume = int(args[0]) / 100
<<<<<<< HEAD
        if 0 < new_volume < 1:
            instance.source.volume = new_volume
        else:
=======
        if 0 < new_volume < 100:
>>>>>>> 613e1cfb008483c3f0d91663588a8b8e56337a1e
            await msg.channel.send(
                embed=utils.create_embed('Volume level must be between 0 and 100, not {0}'.format(new_volume)),
                delete_after=WAIT_UNTIL_DELETE
            )
