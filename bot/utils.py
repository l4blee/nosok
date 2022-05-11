from copy import deepcopy
from typing import Callable, Any, Union

from discord import Colour, Embed
from discord.ext import commands
from discord_components import Button, ButtonStyle, Component

import exceptions
from base import ERROR_COLOR


async def send_embed(ctx: commands.Context, description: str, color: Colour, title: str = '') -> Embed:
    # TODO: Implement different languages support 
    embed = Embed(
        description=description,
        title=title,
        color=color
    )

    return await ctx.send(embed=embed)


async def is_connected(ctx: commands.Context):
    if ctx.invoked_with == 'help' or ctx.voice_client is not None:
        return True

    raise exceptions.BotNotConnected


COMPONENTS = {
    'search': lambda length, current: [
        [
            Button(
                id='back',
                emoji='◀'
            ),
            Button(
                label=f'Page {current + 1}/{length}',
                id='cur',
                disabled=True
            ),
            Button(
                id='forward',
                emoji='▶'
            )
        ],
        [
            Button(label=' ', disabled=True),
            Button(
                label='Add this',
                id='lock',
                style=ButtonStyle.green
            ),
            Button(label=' ', disabled=True)
        ]
    ],
    'playlist': [[
        Button(
            label='Rename',
            id='rename'
        ),
        Button(
            label='Load',
            id='load',
            style=ButtonStyle.green
        ),
        Button(
            label='Delete',
            id='delete',
            style=ButtonStyle.red
        )
    ]]
}


def get_components(name: str) -> Union[list[Component], Callable]:
    return deepcopy(COMPONENTS[name])
