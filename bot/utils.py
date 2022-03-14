import functools
import typing

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle

import exceptions
from base import ERROR_COLOR


async def send_embed(ctx: commands.Context, description: str, color: discord.Colour, title: str = ''):
    embed = discord.Embed(
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


async def run_blocking(blocking_func: typing.Callable, bot: commands.Bot, *args, **kwargs) -> typing.Any:
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)


def get_components(embeds, current):
    return [
        [
            Button(
                label='Back',
                id='back',
                style=ButtonStyle.red
            ),
            Button(
                label=f'Page {current + 1} / {len(embeds)}',
                id='cur',
                style=ButtonStyle.grey,
                disabled=True
            ),
            Button(
                label='Next',
                id='forward',
                style=ButtonStyle.red
            )
        ],
        [
            Button(
                label='Add this',
                id='lock',
                style=ButtonStyle.green
            )
        ]
    ]
