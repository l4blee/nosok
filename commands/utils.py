from json import load
from discord import Embed, Colour


def get_prefix(msg):
    id = msg.guild.id
    with open('config/servers.json', 'r') as file:
        cfg = load(file)
        if str(id) in cfg.keys() and 'prefix' in cfg[str(id)]:
            return cfg[str(id)]['prefix']
        else:
            return '!'


def create_embed(content: str, title: str = None, thumbnail: str = None):
    embed = Embed(color=Colour.from_rgb(209, 178, 25))
    embed.description = content
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if title is not None:
        embed.set_author(name=title)

    return embed
