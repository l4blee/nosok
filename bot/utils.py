from copy import deepcopy
from typing import Callable, Any, Union

from discord import Colour, Embed
from discord.ui import View
from discord.ext import commands

import exceptions
import views
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

    raise exceptions.BotNotConnected


VIEWS = {
    'search': views.Search,
    'playlist': views.Playlist
}


def get_components(name: str) -> View:
    return deepcopy(VIEWS[name])