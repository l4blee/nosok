from commands import utils
import json
import discord
from os import getenv

DELETE_DELAY = float(getenv('DELETE_DELAY'))


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
        desc = desc[lang]
        aliases = [f'`{prefix}{i}`' for i in aliases]
        value = desc + ('\n`Aliases:` ' + ', '.join(aliases) if aliases else '')
        embed.add_field(name=f'`{prefix}{cmd}`', value=value, inline=False)

    await msg.channel.send(embed=embed)


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
