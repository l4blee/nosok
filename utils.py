import discord
from discord.ext import commands
from base import ERROR_COLOR
import exceptions


async def send_embed(description: str, color: discord.Colour, ctx: commands.Context, title: str = ''):
    embed = discord.Embed(
        title=title,
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
        return False
    else:
        return True
=======
import asyncio
import typing
import functools

from bot import MusicBot


async def run_blocking(blocking_func: typing.Callable, bot: MusicBot, *args, **kwargs) -> typing.Any:
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)
