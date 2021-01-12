from commands import utils
import json
import discord
from os import getenv

WAIT_UNTIL_DELETE = float(getenv('WAIT_UNTIL_DELETE'))


async def help(args, msg):
    prefix = utils.get_prefix(msg.guild.id)

    with open('./config/descriptions.json', 'r') as f:
        cmds = json.load(f)

    embed = discord.Embed(colour=discord.Colour.from_rgb(209, 178, 25))
    embed.set_author(name='Available commands', icon_url='https://clck.ru/SWD2D')
    embed.set_thumbnail(url='https://clck.ru/SVDqZ')
    for cmd in cmds.keys():
        embed.add_field(name=f'`{prefix}{cmd}`', value=cmds[cmd], inline=False)
    await msg.channel.send(embed=embed, delete_after=WAIT_UNTIL_DELETE)


async def set_prefix(args, msg):
    new_prefix = args[0]
    if not new_prefix:
        await msg.channel.send('Please specify the prefix you want to set', delete_after=WAIT_UNTIL_DELETE)
        return -1

    guild_id = msg.guild.id
    with open('./config/servers.json', 'r') as f:
        cfg = json.load(f)

    cfg[str(guild_id)] = dict() if guild_id not in cfg.keys() else cfg[str(guild_id)]
    cfg[str(guild_id)]['prefix'] = new_prefix
    with open('./config/servers.json', 'w') as f:
        json.dump(cfg, f, indent=4)

    await msg.channel.send(f'Prefix has been successfully changed to `{new_prefix}`', delete_after=WAIT_UNTIL_DELETE)
