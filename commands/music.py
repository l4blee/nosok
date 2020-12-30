from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos
import discord
import os
from collections import defaultdict
from asyncio import get_running_loop, run_coroutine_threadsafe, sleep
from utils import get_prefix


class QueueElement:
    def __init__(self, title: str, url: str, added_by: discord.Member.mention):
        self.title = title
        self.url = url
        self.added_by = added_by

    def __repr__(self):
        return str(self.title)


class SongQueue:
    __queue = list()
    now_playing = -1

    def __init__(self):
        self.repeat = False
        self.play_after = True

    def add_song(self, title: str, url: str, mentionable: discord.Member.mention):
        song = QueueElement(title, url, mentionable)
        self.__queue.append(song)

    def __next__(self):
        if not self.__queue:
            return None

        self.now_playing += 1
        if self.now_playing >= len(self.__queue):
            if self.repeat:
                self.now_playing = 0
            else:
                return 'Repeat = False'

        return self.__queue[self.now_playing]

    def __getitem__(self, item):
        return self.__queue[item]

    def __repr__(self):
        return ' '.join(self.__queue)


class Music:
    __queues = defaultdict(SongQueue)

    def __init__(self, client):
        self.__client = client

    async def main(self, argv, msg, command):
        if command == 'play':
            await self.play(argv, msg)
        elif command == 'join':
            await self.join(msg)
        elif command == 'leave':
            await self.leave(msg)
        elif command == 'search':
            self.search(argv)
        elif command == 'queue':
            await self.queue(argv, msg)
        elif command == 'stop':
            await self.stop(msg)
        elif command == 'repeat':
            await self.repeat(msg)

    @staticmethod
    def get_voice_instance(msg: discord.Message, client: discord.client):
        for voice_client in client.voice_clients:
            if voice_client.guild.id == msg.guild.id:
                return voice_client
        else:
            return None

    @staticmethod
    def search(argv: list):
        search = SearchVideos(' '.join(argv), max_results=5, mode='dict')
        links = [i['link'] for i in search.result()['search_result']]

        return links

    async def create_ytdl_source(self, url: str, path: os.path):
        if os.path.isfile(path):
            os.remove(path)

        YoutubeDL({
            'format': 'bestaudio/best',
            'extractaudio': True,
            'quiet': True,
            'outtmpl': path
        }).download([url])

        source = discord.FFmpegPCMAudio(path)
        source = discord.PCMVolumeTransformer(source)

        return source

    async def join(self, msg):
        voice = msg.author.voice
        if voice:
            voice_clients = [i.guild.id for i in self.__client.voice_clients]
            if msg.guild.id in voice_clients:
                await msg.channel.send('I am already connected to a voice channel!')
            else:
                await voice.channel.connect()
        else:
            await msg.channel.send('Connect to a voice channel first')

    async def leave(self, msg):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            await instance.disconnect()
        else:
            await msg.channel.send('I am not connected to a voice channel yet!')

    async def __now_playing(self, channel, song: QueueElement):
        info = YoutubeDL({'quiet': True}).extract_info(song.url, download=False)
        embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25)
                              ).set_thumbnail(url=info['thumbnails'][0]['url']
                                              ).set_author(name='Now playing:')
        embed.description = f'[{info["title"]}]({song.url})'
        await channel.send(embed=embed)

    async def play(self, argv, msg, repeat=True):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            this_queue = self.__queues[msg.guild.id]

            if not this_queue and not argv:
                await msg.channel.send('Please specify a url/title of a track you want to play')
                return -1

            instance = self.get_voice_instance(msg, self.__client)
            if argv:
                url = self.search(argv)[0]
                info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
                this_queue.add_song(info['title'], url, msg.author.mention)

                if instance.is_playing():
                    embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25))
                    embed.description = f'Queued [{info["title"]}]({url})'
                    await msg.channel.send(embed=embed)

            if not instance.is_playing():
                song = next(this_queue)
                if not isinstance(song, QueueElement):
                    if song is None:
                        await msg.channel.send('Queue is empty, add something')
                        return -1
                    elif isinstance(song, str):
                        prefix = get_prefix(msg)
                        await msg.channel.send(f'Use command `{prefix}repeat` to enable queue repeating')
                        return -1

                loop = get_running_loop()

                filepath = os.path.relpath(f'downloads/{msg.guild.id}.mp3')
                source = await self.create_ytdl_source(song.url, filepath)
                instance.play(source, after=lambda e: self.__after([], msg, loop))

                await self.__now_playing(msg.channel, song)
        elif repeat:
            await self.join(msg)
            await self.play(argv, msg, repeat=False)

    def __after(self, argv, msg, loop):
        queue = self.__queues[msg.guild.id]
        if queue.play_after:
            run_coroutine_threadsafe(self.play(argv, msg), loop)

    async def queue(self, argv, msg):
        if argv:
            url = self.search(argv)[0]
            info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
            self.__queues[msg.guild.id].add_song(info['title'], url, msg.author.mention)

            embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25))
            embed.description = f'Queued [{info["title"]}]({url})'
            await msg.channel.send(embed=embed)
        else:
            desc = str()
            for song in self.__queues[msg.guild.id]:
                desc += f'[{song.title}]({song.url}) [{song.added_by}]\n'
            else:
                embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25)
                                      ).set_author(name='Current playlist:')
                embed.description = desc
                await msg.channel.send(embed=embed)

    async def stop(self, msg):
        instance = self.get_voice_instance(msg, self.__client)
        queue = self.__queues[msg.guild.id]
        queue.play_after = False

        if instance:
            instance.stop()
            await sleep(0.5)
            queue.play_after = True
            queue.now_playing = -1
        else:
            await msg.channel.send('I am not connected to a voice channel yet')

    async def pause(self, msg):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            instance.pause()
        else:
            await msg.channel.send('I am not connected to a voice channel yet')

    async def resume(self, msg):
        instance = self.get_voice_instance(msg, self.__client)

        if instance:
            instance.resume()
        else:
            await msg.channel.send('I am not connected to a voice channel yet')

    async def clear(self, msg):
        queue = self.__queues[msg.guild.id]
        queue = SongQueue()

    async def repeat(self, msg):
        queue = self.__queues[msg.guild.id]
        queue.repeat = not queue.repeat

        await msg.channel.send('Queue repeating has been successfully ' + ['disabled', 'enabled'][queue.repeat])
