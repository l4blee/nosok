import asyncio
import typing
import functools

from bot import MusicBot


async def run_blocking(blocking_func: typing.Callable, bot: MusicBot, *args, **kwargs) -> typing.Any:
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)
