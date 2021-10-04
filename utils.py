import functools
import typing

import discord
from discord.ext import commands

import exceptions
from base import ERROR_COLOR


async def send_embed(description: str, color: discord.Colour, ctx: commands.Context, title: str = ''):
    embed = discord.Embed(
        description=description,
        color=color
    )
    await ctx.send(embed=embed)


async def is_connected(ctx: commands.Context):
    if ctx.voice_client is None:
        await send_embed(
            ctx=ctx,
            description='I am not connected to a voice channel yet!',
            color=ERROR_COLOR
        )
        raise exceptions.BotNotConnected
    else:
        return True


async def run_blocking(blocking_func: typing.Callable, bot: commands.Bot, *args, **kwargs) -> typing.Any:
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)
