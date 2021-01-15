import discord
from os import getenv
import commands
from commands import utils
import asyncio
from youtube_dl import YoutubeDL
from typing import Union
from urllib.parse import urlparse
from youtubesearchpython import SearchVideos

client = discord.Client()
music = commands.MusicClient(client, ytdl_opts={
    'format': 'worstaudio/worst',
    'quiet': True
})

DELETE_DELAY = float(getenv('DELETE_DELAY'))

# ---- Defining music commands ----
@music.command(aliases=['j'])
async def join(args: list, msg: discord.Message):
    if msg.author.voice:
        if msg.guild.id in [i.guild.id for i in client.voice_clients]:
            await msg.channel.send(
                embed=utils.create_embed('I am already connected to a voice channel!'),
                delete_after=DELETE_DELAY)
        else:
            await msg.author.voice.channel.connect()
    else:
        await msg.channel.send(
            embed=utils.create_embed('Connect to a voice channel first'),
            delete_after=DELETE_DELAY
        )


@music.command(aliases=['l'])
async def leave(args: list, msg: Union[discord.Message, discord.Member]):
    instance = music.get_voice_instance(msg.guild.id)
    if instance:
        if instance.is_playing():
            await music.stop(args, msg)
        await instance.disconnect()
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet!'),
            delete_after=DELETE_DELAY)


@music.command()
async def search(args: list, msg: discord.Message):
    if urlparse(args[0]).scheme != '':
        return args[0]

    result = SearchVideos(' '.join(args), max_results=5, mode='dict').result()['search_result']
    links = [i['link'] for i in result]

    return links[0]


@music.command(aliases=['pl', 'p'])
async def play(args: list, msg: discord.Message, repeat=True, skipped=True):
    instance = music.get_voice_instance(msg.guild.id)
    prefix = utils.get_prefix(msg.guild.id)

    if instance:
        this_queue = music.queues[msg.guild.id]

        if not this_queue and not args:
            await msg.channel.send(
                embed=utils.create_embed('Please specify a url/title of a track you want to play'),
                delete_after=DELETE_DELAY)
            return

        if args:
            url = await music.search(args, msg)
            info = YoutubeDL(music.YTDL_OPTS).extract_info(url, download=False)
            this_queue.add_song(info['title'], url, msg.author.mention)

            if instance.is_playing():
                await msg.channel.send(
                    embed=utils.create_embed(f'Queued [{info["title"]}]({url})'),
                    delete_after=DELETE_DELAY)

            if not instance.is_playing():
                this_queue.now_playing = len(this_queue) - 2

        if not instance.is_playing() and not instance.is_paused():
            song = next(this_queue)
            if not isinstance(song, commands.QueueElement):
                if song is None:
                    await msg.channel.send(
                        embed=utils.create_embed('Queue is empty, add something'),
                        delete_after=DELETE_DELAY)
                    return
                elif song == -1:
                    await msg.channel.send(
                        embed=utils.create_embed(f'Use command `{prefix}repeat` to enable queue repeating'),
                        delete_after=DELETE_DELAY)
                    return

            loop = asyncio.get_running_loop()
            source, info = music.create_ytdl_source(song.url)
            notification = await msg.channel.send(
                embed=utils.create_embed(f'[{info["title"]}]({song.url})', 'Now playing:', info['thumbnails'][0]['url'])
            )
            instance.play(source, after=lambda e: after_play(msg, loop, notification))

            if skipped:
                this_queue.play_after = True
        elif instance.is_paused():
            await msg.channel.send(
                embed=utils.create_embed(f'Current track is paused, type `{prefix}resume` or `{prefix}stop`'),
                delete_after=DELETE_DELAY)
    elif repeat:
        await music.join(list(), msg)
        await music.play(args, msg, repeat=False)


def after_play(msg: discord.Message, loop: asyncio.AbstractEventLoop, notification: discord.Message):
    if music.queues[msg.guild.id].play_after:
        asyncio.run_coroutine_threadsafe(music.play(list(), msg), loop)

    asyncio.run_coroutine_threadsafe(notification.delete(), loop)


@music.command(aliases=['st'])
async def stop(args: list, msg: discord.Message):
    instance = music.get_voice_instance(msg.guild.id)
    queue = music.queues[msg.guild.id]

    if instance:
        queue.play_after = False
        instance.stop()
        await asyncio.sleep(0.1)
        queue.play_after, queue.now_playing = True, -1
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY)


@music.command(aliases=['q'])
async def queue(args: list, msg: discord.Message):
    current_queue = music.queues[msg.guild.id]

    if args:
        url = await search(args, msg)
        info = YoutubeDL(music.YTDL_OPTS).extract_info(url, download=False)
        current_queue.add_song(info['title'], url, msg.author.mention)

        await msg.channel.send(
            embed=utils.create_embed(f'Queued [{info["title"]}]({url})'),
            delete_after=DELETE_DELAY)
    else:
        desc = str()
        for index, song in zip(range(1, len(current_queue) + 1), current_queue):
            desc += f'{index}. [{song.title}]({song.url}) [{song.added_by}]\n'

        await msg.channel.send(
            embed=utils.create_embed(desc, title='Current playlist:'),
            delete_after=DELETE_DELAY)


@music.command(aliases=['c'])
async def clear(args: list, msg: discord.Message):
    queue = music.queues[msg.guild.id]
    for _ in range(len(queue)):
        queue.remove_song(0)

    await msg.channel.send(
        embed=utils.create_embed('Queue has been successfully cleared'),
        delete_after=DELETE_DELAY)


@music.command(aliases=['rm'])
async def remove(args: list, msg: discord.Message):
    if not args or not args[0].isnumeric():
        await msg.channel.send(
            embed=utils.create_embed('Please specify the track you want to remove form the queue'),
            delete_after=DELETE_DELAY)
        return

    res = music.queues[msg.guild.id].remove_song(int(args[0]) - 1)
    if not isinstance(res, commands.QueueElement):
        await msg.channel.send(
            embed=utils.create_embed('Please specify index of a track in the queue'),
            delete_after=DELETE_DELAY)
    else:
        await msg.channel.send(
            embed=utils.create_embed(f'[{res.title}]({res.url}) has been successfully removed form the queue'),
            delete_after=DELETE_DELAY)


@music.command()
async def skip(args: list, msg: discord.Message):
    instance = music.get_voice_instance(msg.guild.id)

    if not instance:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY
        )
        return

    if instance.is_playing():
        instance.stop()
        music.queues[msg.guild.id].play_after = False
        await music.play(list(), msg, skipped=True)


@music.command(aliases=['rep'])
async def repeat(args: list, msg: discord.Message):
    queue = music.queues[msg.guild.id]
    queue.repeat = not queue.repeat

    await msg.channel.send(
        embed=utils.create_embed(f'Queue repeating has been successfully `{["disabled", "enabled"][queue.repeat]}`'),
        delete_after=DELETE_DELAY)


@music.command()
async def pause(args: list, msg: discord.Message):
    instance = music.get_voice_instance(msg.guild.id)

    if instance:
        if instance.is_paused():
            await msg.channel.send(
                embed=utils.create_embed('Audio is already paused'),
                delete_after=DELETE_DELAY)
        else:
            instance.pause()
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY)


@music.command(aliases=['res'])
async def resume(args: list, msg: discord.Message):
    instance = music.get_voice_instance(msg.guild.id)

    if instance:
        if instance.is_playing():
            await msg.channel.send(
                embed=utils.create_embed('Audio is already playing'),
                delete_after=DELETE_DELAY)
        else:
            instance.resume()
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY)


@music.command(aliases=['vol'])
async def volume(args: list, msg: discord.Message):
    instance = music.get_voice_instance(msg.guild.id)

    if not instance:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY
        )
        return -1

    volume = int(args[0])
    if 0 <= volume <= 100:
        instance.source.volume = volume / 100
    else:
        await msg.channel.send(
            embed=utils.create_embed(f'Volume level must be between `0` and `100`, not `{volume}`'),
            delete_after=DELETE_DELAY
        )


CMDS_BY_TYPES = {
    'commands': {
        'help',
        'set_prefix'
    },
    'music': set(filter(lambda s: not s.startswith('_'), music.__dict__))
}

CMDS = set()
for i in CMDS_BY_TYPES.values():
    CMDS = CMDS.union(i)

# ---- Defining discord client methods ----
@client.event
async def on_ready():
    print(f'{client.user} has been successfully launched!')


@client.event
async def on_message(msg):
    prefix = commands.utils.get_prefix(msg.guild.id)
    if msg.content.startswith(prefix) and msg.author.id is not client.user.id:
        cmd, *args = msg.content[len(prefix):].split(' ').strip()
        cmd = cmd.lower()

        print(f'Detected command "{cmd}" on server {msg.guild.id}')
        if cmd not in CMDS:
            await msg.channel.send(
                embed=commands.utils.create_embed(f'There is no such a command.'
                                                  f' Type `{prefix}help` to get a list of available commands.'),
                delete_after=DELETE_DELAY
            )
        else:
            cmd_type = [i[0] for i in CMDS_BY_TYPES.items() if cmd in i[1]][0]
            await eval(f'{cmd_type}.{cmd}(args, msg)')


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    if member.id != client.user.id:
        inst = music.get_voice_instance(member.guild.id)
        members = inst.channel.members
        if len(members) == 1 and members[0].id == client.user.id:
            await music.leave([], member)


client.run(getenv('BOT_TOKEN'))
