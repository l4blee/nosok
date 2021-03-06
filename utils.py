from json import load
from discord import Embed, Colour


def get_prefix(guild_id):
    with open('config/servers.json', 'r') as file:
        try:
            return load(file).get(str(guild_id)).get('prefix')
        except AttributeError:
            return '!'


def create_embed(content: str, title: str = None, thumbnail: str = None, embed_type: str = 'success'):
    if embed_type == 'success':
        color = Colour.from_rgb(209, 178, 25)
    elif embed_type == 'error':
        color = Colour.from_rgb(220, 20, 60)
    else:
        raise TypeError('Unexpected embed type')

    embed = Embed(color=color)
    embed.description = content
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)

    if title is not None:
        embed.set_author(name=title)

    return embed
