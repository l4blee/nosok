import discord
from os import getenv
from utils import get_prefix, create_embed
from commands import music, help, set_prefix

client = discord.Client()
music_client = music.Music(client)

CMDS = {'music': music_client.CMDS,
        'other': {'help', 'set_prefix'}}

ALL_CMDS = list()
for i in CMDS.values():
    ALL_CMDS.extend(i)
ALL_CMDS = set(ALL_CMDS)


@client.event
async def on_ready():
    print(f'{client.user} has been successfully launched!')


@client.event
async def on_message(msg):
    prefix = get_prefix(msg)
    if msg.content.startswith(prefix) and msg.author.id is not client.user.id:
        cmd, *args = msg.content[len(prefix):].split(' ')
        cmd = cmd.lower()
        args = tuple(args)

        print('Detected command "' + cmd + '" on server', msg.guild.id)
        if cmd not in ALL_CMDS:
            await msg.channel.send(embed=create_embed(f'There is no such a command.'
                                   f' Type `{prefix}help` to get a list of available commands.'))
        else:
            if cmd in CMDS['music']:
                await music_client.main(args, msg, cmd)
            else:
                await eval(f'{cmd}.main(args, msg)')


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    if not member.id == client.user.id:
        if isinstance(before.channel, discord.VoiceChannel):
            members = before.channel.members
            if len(members) == 1 and members[0].id == client.user.id:
                await music_client.leave(tuple(), member)


client.run(getenv('BOT_TOKEN'))
