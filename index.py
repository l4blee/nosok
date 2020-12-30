import discord
from os import getenv
import utils
from commands import music, help, set_prefix

CMDS = {'music': ('search', 'play', 'join', 'leave', 'queue', 'repeat', 'stop', 'pause', 'resume'),
        'other': ('help', 'set_prefix')}

ALL_CMDS = list()
for i in CMDS.values():
    ALL_CMDS.extend(i)
ALL_CMDS = set(ALL_CMDS)

client = discord.Client()
music_client = music.Music(client)


@client.event
async def on_ready():
    print(f'{client.user} has been successfully launched!')
    await client.change_presence(activity=discord.Game('!help'))


@client.event
async def on_message(msg):
    prefix = utils.get_prefix(msg)
    if msg.content.startswith(prefix) and msg.author.id is not client.user.id:
        cmd, *argv = msg.content[len(prefix):].split(' ')

        print('Detected command "' + cmd + '" on server', msg.guild.id)
        if cmd not in ALL_CMDS:
            await msg.channel.send('There is no such a command. Type `!help` to get a list of available commands.')
        else:
            if cmd in CMDS['music']:
                await music_client.main(argv, msg, cmd)
            else:
                await eval(f'{cmd}.main(argv, msg)')


client.run(getenv('BOT_TOKEN'))
