import discord
import utils
import asyncio
import json
import core
import os
from typing import Union
from urllib.parse import urlparse
from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos

client = core.Client(ytdl_opts={
    'format': 'worstaudio/worst',
    'quiet': True
})

DELETE_DELAY = float(os.getenv('DELETE_DELAY'))

# ---- Defining music commands ----
@client.command(aliases=['j'])
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


@client.command(aliases=['l'])
async def leave(args: list, msg: Union[discord.Message, discord.Member]):
    instance = client.get_voice_instance(msg.guild.id)
    if instance:
        if instance.is_playing():
            await client.stop(args, msg)
        await instance.disconnect()
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet!'),
            delete_after=DELETE_DELAY)


@client.command()
async def search(args: list, msg: discord.Message):
    if urlparse(args[0]).scheme != '':
        return args[0]

    result = SearchVideos(' '.join(args), max_results=5, mode='dict').result()['search_result']
    links = [i['link'] for i in result]

    return links[0]


@client.command(aliases=['pl', 'p'])
async def play(args: list, msg: discord.Message, repeat=True, skipped=True):
    instance = client.get_voice_instance(msg.guild.id)
    prefix = utils.get_prefix(msg.guild.id)

    if instance:
        this_queue = client.queues[msg.guild.id]

        if not this_queue and not args:
            await msg.channel.send(
                embed=utils.create_embed('Please specify a url/title of a track you want to play'),
                delete_after=DELETE_DELAY)
            return

        if args:
            url = await client.search(args, msg)
            info = YoutubeDL(client.YTDL_OPTS).extract_info(url, download=False)
            this_queue.add_song(info['title'], url, msg.author.mention)

            if instance.is_playing():
                await msg.channel.send(
                    embed=utils.create_embed(f'Queued [{info["title"]}]({url})'),
                    delete_after=DELETE_DELAY)

            if not instance.is_playing():
                this_queue.now_playing = len(this_queue) - 2

        if not instance.is_playing() and not instance.is_paused():
            song = next(this_queue)
            if not isinstance(song, core.QueueElement):
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
            source, info = client.create_ytdl_source(song.url)
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
        await client.join(list(), msg)
        await client.play(args, msg, repeat=False)


def after_play(msg: discord.Message, loop: asyncio.AbstractEventLoop, notification: discord.Message):
    if client.queues[msg.guild.id].play_after:
        asyncio.run_coroutine_threadsafe(client.play(list(), msg), loop)

    asyncio.run_coroutine_threadsafe(notification.delete(), loop)


@client.command(aliases=['st'])
async def stop(args: list, msg: discord.Message):
    instance = client.get_voice_instance(msg.guild.id)
    queue = client.queues[msg.guild.id]

    if instance:
        queue.play_after = False
        instance.stop()
        await asyncio.sleep(0.1)
        queue.play_after, queue.now_playing = True, -1
    else:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY)


@client.command(aliases=['q'])
async def queue(args: list, msg: discord.Message):
    current_queue = client.queues[msg.guild.id]

    if args:
        url = await search(args, msg)
        info = YoutubeDL(client.YTDL_OPTS).extract_info(url, download=False)
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


@client.command(aliases=['c'])
async def clear(args: list, msg: discord.Message):
    queue = client.queues[msg.guild.id]
    for _ in range(len(queue)):
        queue.remove_song(0)

    await msg.channel.send(
        embed=utils.create_embed('Queue has been successfully cleared'),
        delete_after=DELETE_DELAY)


@client.command(aliases=['rm'])
async def remove(args: list, msg: discord.Message):
    if not args or not args[0].isnumeric():
        await msg.channel.send(
            embed=utils.create_embed('Please specify the track you want to remove form the queue'),
            delete_after=DELETE_DELAY)
        return

    res = client.queues[msg.guild.id].remove_song(int(args[0]) - 1)
    if not isinstance(res, core.QueueElement):
        await msg.channel.send(
            embed=utils.create_embed('Please specify index of a track in the queue'),
            delete_after=DELETE_DELAY)
    else:
        await msg.channel.send(
            embed=utils.create_embed(f'[{res.title}]({res.url}) has been successfully removed form the queue'),
            delete_after=DELETE_DELAY)


@client.command()
async def skip(args: list, msg: discord.Message):
    instance = client.get_voice_instance(msg.guild.id)

    if not instance:
        await msg.channel.send(
            embed=utils.create_embed('I am not connected to a voice channel yet'),
            delete_after=DELETE_DELAY
        )
        return

    if instance.is_playing():
        instance.stop()
        client.queues[msg.guild.id].play_after = False
        await client.play(list(), msg, skipped=True)


@client.command(aliases=['rep'])
async def repeat(args: list, msg: discord.Message):
    queue = client.queues[msg.guild.id]
    queue.repeat = not queue.repeat

    await msg.channel.send(
        embed=utils.create_embed(f'Queue repeating has been successfully `{["disabled", "enabled"][queue.repeat]}`'),
        delete_after=DELETE_DELAY)


@client.command()
async def pause(args: list, msg: discord.Message):
    instance = client.get_voice_instance(msg.guild.id)

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


@client.command(aliases=['res'])
async def resume(args: list, msg: discord.Message):
    instance = client.get_voice_instance(msg.guild.id)

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


@client.command(aliases=['vol'])
async def volume(args: list, msg: discord.Message):
    instance = client.get_voice_instance(msg.guild.id)

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


@client.command(aliases=['h'])
async def help(args, msg):
    prefix = utils.get_prefix(msg.guild.id)
    lang = args[0] if args else 'en'

    with open('./config/descriptions.json', 'r', encoding='utf-8') as f:
        cmds = json.load(f)

    embed = discord.Embed(colour=discord.Colour.from_rgb(209, 178, 25))
    embed.set_author(name='Available commands', icon_url='https://clck.ru/SWD2D')
    embed.set_thumbnail(url='https://clck.ru/SVDqZ')
    for cmd in cmds.keys():
        desc, aliases = cmds[cmd]
        desc = desc[lang] if lang in desc else 'en'
        aliases = [f'`{prefix}{i}`' for i in aliases]
        value = desc + ('\n`Aliases:` ' + ', '.join(aliases) if aliases else '')
        embed.add_field(name=f'`{prefix}{cmd}`', value=value, inline=False)

    await msg.channel.send(embed=embed)


@client.command(aliases=['prefix', 'setprefix'])
async def set_prefix(args, msg):
    new_prefix = args[0]
    if not new_prefix:
        await msg.channel.send(
            embed=utils.create_embed('Please specify the prefix you want to set'),
            delete_after=DELETE_DELAY)
        return

    guild_id = msg.guild.id
    with open('./config/servers.json', 'r') as f:
        cfg = json.load(f)

    cfg[str(guild_id)] = cfg.get(str(guild_id)) or dict()
    cfg[str(guild_id)]['prefix'] = new_prefix
    with open('./config/servers.json', 'w') as f:
        json.dump(cfg, f, indent=4)

    await msg.channel.send(
        embed=utils.create_embed(f'Prefix has been successfully changed to `{new_prefix}`'),
        delete_after=DELETE_DELAY)


# ---- Defining discord client methods ----
@client.event
async def on_ready():
    print(f'{client.user} has been successfully launched!')


@client.event
async def on_message(msg):
    prefix = utils.get_prefix(msg.guild.id)
    if msg.content.startswith(prefix) and msg.author.id is not client.user.id:
        cmd, *args = msg.content[len(prefix):].split(' ')
        cmd = cmd.lower()

        print(f'Detected command "{cmd}" on server {msg.guild.id}')
        if not hasattr(client, cmd):
            await msg.channel.send(
                embed=utils.create_embed(f'There is no such a command.'
                                                  f' Type `{prefix}help` to get a list of available commands.'),
                delete_after=DELETE_DELAY
            )
        else:
            await eval(f'client.{cmd}(args, msg)')


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    if member.id != client.user.id:
        inst = client.get_voice_instance(member.guild.id)
        members = inst.channel.members
        if len(members) == 1 and members[0].id == client.user.id:
            inst.leave([], member)


if __name__ == '__main__':
    client.run(os.getenv('BOT_TOKEN'))
