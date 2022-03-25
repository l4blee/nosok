from functools import partial
from copy import deepcopy
from typing import Callable, Any, Union

from discord import Colour, Embed
from discord.ext import commands
from discord_components import Button, ButtonStyle, Component

import exceptions
from base import ERROR_COLOR


async def send_embed(ctx: commands.Context, description: str, color: Colour, title: str = '') -> Embed:
    embed = Embed(
        description=description,
        title=title,
        color=color
    )

    return await ctx.send(embed=embed)


async def is_connected(ctx: commands.Context):
    if ctx.invoked_with == 'help' or ctx.voice_client is not None:
        return True

    await send_embed(
        ctx=ctx,
        description='I am not connected to a voice channel yet!',
        color=ERROR_COLOR
    )
    raise exceptions.BotNotConnected


async def run_blocking(blocking_func: Callable, bot: commands.Bot, *args, **kwargs) -> Any:
    func = partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)


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
            id='load'
        ),
        Button(
            label='Delete',
            id='delete'
        )
    ]]
}


def get_components(name: str) -> Union[list[Component], Callable]:
    return deepcopy(COMPONENTS[name])
