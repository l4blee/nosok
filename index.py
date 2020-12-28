import discord
from os import getenv
import utils
from commands import *
from commands import __all__ as cmds

client = discord.Client()


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
        if cmd in cmds:
            await eval(f'{cmd}.main(argv, msg)')
        else:
            if await music.__main(argv, msg, cmd, client):
                await msg.channel.send('There is no such a command. Type `!help` to get a list of available commands.')


client.run(getenv('BOT_TOKEN'))
