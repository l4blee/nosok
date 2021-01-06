from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos
import discord
from collections import defaultdict
import asyncio
from utils import get_prefix, create_embed
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


class Music:
    __queues = defaultdict(SongQueue)
    CMDS = {
        'play',
        'join',
        'leave',
        'stop',
        'search',
        'queue',
        'repeat',
        'pause',
        'resume',
        'clear',
        'skip'
    }

    def __init__(self, client):
        self.__client = client

    async def main(self, args: tuple, msg: discord.Message, command: str):
        await eval(f'self.{command}(args, msg)')

    @staticmethod
    def get_voice_instance(msg: discord.Message, client: discord.client):
        for voice_client in client.voice_clients:
            if voice_client.guild.id == msg.guild.id:
                return voice_client
        else:
            return None

    async def create_ytdl_source(self, source_url: str):
        url = YoutubeDL({
            'format': 'bestaudio/best',
            'quiet': True,
        }).extract_info(source_url, download=False)['formats'][0]['url']

        source = discord.FFmpegPCMAudio(url, stderr=DEVNULL,
                                        before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        source = discord.PCMVolumeTransformer(source)
        return source

    async def now_playing(self, channel: discord.TextChannel, song: QueueElement):
        info = YoutubeDL({'quiet': True}).extract_info(song.url, download=False)
        return await channel.send(
            embed=create_embed(f'[{info["title"]}]({song.url})', 'Now playing:', info['thumbnails'][0]['url'])
        )

    async def search(self, args: tuple, msg: discord.Message, return_to_user=True):
        if urlparse(args[0]).scheme != '':
            return args[0]

        search = SearchVideos(' '.join(args), max_results=5, mode='dict')
        links = [i['link'] for i in search.result()['search_result']]

        if return_to_user:
            await msg.channel.send(embed=create_embed('\n'.join(links)), delete_after=WAIT_UNTIL_DELETE)

        return links[0]

    async def join(self, args: tuple, msg: discord.Message):
        voice = msg.author.voice
        if voice:
            voice_clients = [i.guild.id for i in self.__client.voice_clients]
            if msg.guild.id in voice_clients:
                embed = create_embed('I am already connected to a voice channel!')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
            else:
                await voice.channel.connect()
        else:
            embed = create_embed('Connect to a voice channel first')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def leave(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg, self.__client)
        if instance:
            await instance.disconnect()
        else:
            embed = create_embed('I am not connected to a voice channel yet!')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def play(self, args: tuple, msg: discord.Message, repeat=True, skipped=True):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            this_queue = self.__queues[msg.guild.id]

            if not this_queue and not args:
                embed = create_embed('Please specify a url/title of a track you want to play')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
                return -1

            instance = self.get_voice_instance(msg, self.__client)
            if args:
                url = await self.search(args, msg, return_to_user=False)
                info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
                this_queue.add_song(info['title'], url, msg.author.mention)

                if instance.is_playing():
                    embed = create_embed(f'Queued [{info["title"]}]({url})')
                    await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

                if not instance.is_playing():
                    this_queue.now_playing = len(this_queue) - 2

            if not instance.is_playing() and not instance.is_paused():
                song = next(this_queue)
                if not isinstance(song, QueueElement):
                    if song is None:
                        embed = create_embed('Queue is empty, add something')
                        await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
                        return -1
                    elif isinstance(song, str):
                        prefix = get_prefix(msg)
                        embed = create_embed(f'Use command `{prefix}repeat` to enable queue repeating')
                        await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
                        return -1

                loop = asyncio.get_running_loop()
                source = await self.create_ytdl_source(song.url)
                notification = await self.now_playing(msg.channel, song)
                instance.play(source, after=lambda e: self.__after(tuple(), msg, loop, notification))

                if skipped:
                    this_queue.play_after = True
            elif instance.is_paused():
                prefix = get_prefix(msg)
                embed = create_embed(f'Current track is paused, type `{prefix}resume` or `{prefix}stop`')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
        elif repeat:
            await self.join(tuple(), msg)
            await self.play(args, msg, repeat=False)

    def __after(self, argv: tuple, msg: discord.Message, loop: asyncio.AbstractEventLoop, notification: discord.Message):
        queue = self.__queues[msg.guild.id]
        if queue.play_after:
            asyncio.run_coroutine_threadsafe(self.play(argv, msg), loop)
        asyncio.run_coroutine_threadsafe(notification.delete(), loop)

    async def queue(self, args: tuple, msg: discord.Message):
        if args:
            url = await self.search(args, return_to_user=False)
            info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
            self.__queues[msg.guild.id].add_song(info['title'], url, msg.author.mention)

            embed = create_embed(f'Queued [{info["title"]}]({url})')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
        else:
            desc = str()
            for song in self.__queues[msg.guild.id]:
                desc += f'[{song.title}]({song.url}) [{song.added_by}]\n'
            else:
                embed = create_embed(desc, title='Current playlist:')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def stop(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg, self.__client)
        queue = self.__queues[msg.guild.id]
        queue.play_after = False

        if instance:
            instance.stop()
            await asyncio.sleep(0.5)
            queue.play_after = True
            queue.now_playing = -1
        else:
            embed = create_embed('I am not connected to a voice channel yet')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def pause(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            if instance.is_paused():
                embed = create_embed('Audio is already paused')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
            else:
                instance.pause()
        else:
            embed = create_embed('I am not connected to a voice channel yet')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def resume(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            if instance.is_playing():
                embed = create_embed('Audio is already playing')
                await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
            else:
                instance.resume()
        else:
            embed = create_embed('I am not connected to a voice channel yet')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def clear(self, args: tuple, msg: discord.Message):
        queue = self.__queues[msg.guild.id]
        for _ in range(len(queue)):
            queue.remove_song(0)

        embed = create_embed('Queue has been successfully cleared')
        await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def repeat(self, args: tuple, msg: discord.Message):
        queue = self.__queues[msg.guild.id]
        queue.repeat = not queue.repeat

        embed = create_embed('Queue repeating has been successfully ' + ['disabled', 'enabled'][queue.repeat])
        await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)

    async def skip(self, args: tuple, msg: discord.Message):
        instance = self.get_voice_instance(msg, self.__client)

        if not instance:
            embed = create_embed('I am not connected to a voice channel yet')
            await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)
            return -1

        if instance.is_playing():
            instance.stop()
            self.__queues[msg.guild.id].play_after = False
            await asyncio.sleep(0.5)
            await self.play(tuple(), msg, skipped=True)
