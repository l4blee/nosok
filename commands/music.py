from utils import get_voice_instance
from youtube_dl import YoutubeDL
import discord
import os
from youtubesearchpython import SearchVideos
from urllib.parse import urlparse
from collections import defaultdict
import asyncio


async def __main(argv, msg, cmd, cli):
    if cmd not in cmds and cmd not in abbreviations:
        return -1

    global client
    client = cli

    if len(cmd) == 1:
        cmd = cmds[abbreviations.index(cmd)]

    await eval(f'{cmd}(argv, msg)')


async def join(argv, msg):
    global client
    voice = msg.author.voice
    text_ch = msg.channel
    if voice:
        ids = [i.guild.id for i in client.voice_clients]
        if msg.guild.id in ids:
            await text_ch.send('I am already connected to a voice channel!')
        else:
            await voice.channel.connect()
    else:
        await text_ch.send('Connect to a voice channel first')


async def leave(argv, msg):
    global client
    instance = get_voice_instance(msg, client)
    if instance:
        await instance.disconnect()
    else:
        await msg.channel.send('I am not connected to a voice channel yet!')


async def play(argv, msg, repeat=True):
    global client, queues, play_after

    if not play_after:
        play_after = True
        return

    instance = get_voice_instance(msg, client)
    if instance:
        # Adding to queue
        this_queue = queues[msg.guild.id]
        if argv:
            url = argv[0] if urlparse(argv[0]).scheme != '' else await search(argv, msg, notify_user=False)
            info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
            this_queue.append((info['title'], url, msg.author.mention))

        if not this_queue:
            await msg.channel.send('Please specify a url/title of a track you want to play')
            return

        if not instance.is_playing():
            title, url, author = this_queue.pop(0)

            # Removing a file of a previous song to downloading a new one
            path = os.path.relpath(f'downloads/{msg.guild.id}.mp3')
            if os.path.isfile(path):
                os.remove(path)

            YoutubeDL({
                'format': 'bestaudio/best',
                'outtmpl': path,
                'quiet': True
            }).download([url])

            # Exact playing an audio
            loop = asyncio.get_running_loop()

            audio = discord.FFmpegPCMAudio(path)
            audio = discord.PCMVolumeTransformer(audio)
            instance.play(audio, after=lambda e: __after([], msg, loop))

            await __now_playing(msg.channel, url)
    elif repeat:
        await join(argv, msg)
        await play(argv, msg, repeat=False)


def __after(argv, msg, loop):
    asyncio.run_coroutine_threadsafe(play(argv, msg), loop)


async def __now_playing(channel, url):
    info = YoutubeDL({'quiet': True}).extract_info(url, download=False)
    
    embed = discord.Embed(title='Now playing: ', colour=discord.Colour.from_rgb(209, 178, 25))
    embed.description = '[{}]({})'.format(info['title'], url)
    embed.set_thumbnail(url=info['thumbnails'][0]['url'])
    await channel.send(embed=embed)


async def stop(argv, msg):
    global client, play_after
    instance = get_voice_instance(msg, client)
    if instance:
        play_after = False
        instance.stop()
        await leave(argv, msg)
    else:
        await msg.channel.send('I am not connected to a voice channel yet!')


async def search(argv, msg, notify_user=True):
    search = SearchVideos(' '.join(argv), max_results=5, mode='dict')

    embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25))
    links = [i['link'] for i in search.result()['search_result']]
    embed.description = '\n'.join(links)

    if notify_user:
        await msg.channel.send(embed=embed)

    return links[0]


async def volume(argv, msg):
    global client
    volume = int(argv[0]) / 100
    instance = get_voice_instance(msg, client)
    if instance:
        if not 0 <= volume <= 1:
            await msg.channel.send('Specify the sound level as a percentage (0 to 100)')
        else:
            instance.source.volume = volume
    else:
        await msg.channel.send('I am not connected to a voice channel yet!')


async def queue(argv, msg):
    global queues

    desc = str()
    for id in queues.keys():
        for song in queues[id]:
            desc += f'[{song[0]}]({song[1]}) [{song[2]}]\n'

    embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25))
    embed.set_author(name='Current playlist:')
    embed.description = desc
    await msg.channel.send(embed=embed)


async def add(argv, msg):
    global queues

    url = argv[0] if urlparse(argv[0]).scheme != '' else await search(argv, msg, notify_user=False)
    title = YoutubeDL({'quiet': True}).extract_info(url, download=False)['title']
    queues[msg.guild.id].append((title, url, msg.author.mention))

    embed = discord.Embed(color=discord.Colour.from_rgb(209, 178, 25))
    embed.description = f'Queued [{title}]({url})'
    await msg.channel.send(embed=embed)


async def skip(argv, msg):
    instance = get_voice_instance(msg, client)
    instance.stop()
    await play(argv, msg)


client = None
queues = defaultdict(list)
play_after = True
cmds = list(filter(lambda x: not x.startswith('__'), dir()))
abbreviations = list(map(lambda x: x[0], cmds))
