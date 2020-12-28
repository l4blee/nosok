from discord import Embed, Colour
from utils import get_prefix
from json import load


async def main(argv, msg):
    prefix = get_prefix(msg)

    with open('./config/descriptions.json', 'r') as f:
        cmds = load(f)

    embed = Embed(colour=Colour.from_rgb(209, 178, 25))
    embed.set_author(name='Available commands', icon_url='https://clck.ru/SWD2D')
    embed.set_thumbnail(url='https://clck.ru/SVDqZ')
    for cmd in cmds.keys():
        embed.add_field(name=f'`{prefix}{cmd}`', value=cmds[cmd], inline=False)
    await msg.channel.send(embed=embed)
