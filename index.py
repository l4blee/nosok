import discord
from os import getenv
import commands


client = discord.Client()
music = commands.MusicClient(client)


@client.event
async def on_ready():
    print(f'{client.user} has been successfully launched!')


@client.event
async def on_message(msg):
    prefix = commands.utils.get_prefix(msg)
    if msg.content.startswith(prefix) and msg.author.id is not client.user.id:
        cmd, *args = msg.content[len(prefix):].split(' ')
        cmd = cmd.lower()
        args = tuple(args)

        print('Detected command "' + cmd + '" on server', msg.guild.id)
        if cmd not in commands.CMDS:
            await msg.channel.send(
                embed=commands.utils.create_embed(f'There is no such a command.'
                                                  f' Type `{prefix}help` to get a list of available commands.')
            )
        else:
            cmd_type = [i[0] for i in commands.CMDS_BY_TYPES.items() if cmd in i[1]][0]
            await eval(f'{cmd_type}.{cmd}(args, msg)')


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    if not member.id == client.user.id:
        if isinstance(before.channel, discord.VoiceChannel):
            members = before.channel.members
            if len(members) == 1 and members[0].id == client.user.id:
                await music.leave(tuple(), member)


client.run(getenv('BOT_TOKEN'))
