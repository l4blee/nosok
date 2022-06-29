import sys
import logging
from time import perf_counter
from pathlib import Path
from traceback import print_exception

import discord
from discord.ext import commands

from base import BASE_PREFIX, ERROR_COLOR
from handlers import YDLHandler, EventHandler, PerformanceProcessor
from exceptions import CustomException
from utils import send_embed

from database import db


class Bot(commands.Bot):
    __slots__ = ('_logger')

    def __init__(self, command_prefix):
        self._start_time = perf_counter()

        intents = discord.Intents.all()
        super().__init__(command_prefix, intents=intents, case_insensitive=True)

        self._logger = logging.getLogger(
            self.__class__.__module__ + '.' + self.__class__.__qualname__)

    async def on_command_error(self, ctx: commands.Context, exception):
        if isinstance(exception, CustomException):
            await send_embed(
                ctx=ctx,
                description=exception.description,
                color=exception.type_.value)
        else:
            if isinstance(exception, commands.CommandNotFound):
                await send_embed(ctx,
                                 f'Command not found, type in `{ctx.prefix}help` to get the list of all the commands available.',
                                 ERROR_COLOR)
            elif isinstance(exception, commands.MissingRequiredArgument):
                await send_embed(ctx,
                                 f'Please provide {exception.param.name}. '
                                 f'Type `{ctx.prefix}help {ctx.invoked_with}` to get help.',
                                 ERROR_COLOR)
            else:
                await send_embed(ctx,
                                 'An error occured during handling this command, please try again later.',
                                 ERROR_COLOR)

                self._logger.warning(
                    f'Ignoring exception in command {ctx.command}, guild: name={ctx.guild.name}, id={ctx.guild.id}:')
                print_exception(type(exception), exception,
                                exception.__traceback__, file=sys.stderr)

    async def setup(self):
        self._logger.info('Loading cogs...')
        for i in Path('bot/cogs/').glob('*.py'):
            await self.load_extension(f'cogs.{i.stem}')

        self._logger.info(f'Available cogs: {", ".join(self.cogs.keys())}')

    async def start(self, *args, **kwargs):
        await self.setup()
        await super().start(*args, **kwargs)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f'music | {BASE_PREFIX}help'))

        performance_processor.start()
        event_handler.start()

        self._logger.info(
            f'The bot has been successfully launched in approximately {round(perf_counter() - self._start_time, 2)}s')
        delattr(self, '_start_time')

    async def close(self):
        self._logger.info('The bot is being shut down...')

        performance_processor.close()
        event_handler.close()

        await super().close()


bot = Bot(db.get_prefix)

performance_processor = PerformanceProcessor(bot)
event_handler = EventHandler(bot)

music_handler = YDLHandler({
    'simulate': True,
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'format': 'bestaudio',
    'skip_download': True,
    'age_limit': 17,
})
