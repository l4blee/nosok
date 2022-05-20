import os
import sys
import logging
from time import perf_counter
from importlib import import_module
from pathlib import Path
from traceback import print_exception

from discord import Game
from discord.ext import commands
from discord_components.client import DiscordComponents

from base import BASE_PREFIX, ERROR_COLOR
from handlers import YDLHandler, EventHandler, DataProcessor
from exceptions import CustomException
from utils import send_embed

from database import db


class Bot(commands.Bot):
    __slots__ = ('_logger')

    def __init__(self, command_prefix):
        self._start_time = perf_counter()
        super().__init__(command_prefix, case_insensitive=True)
        self._logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)

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
                
                self._logger.warning(f'Ignoring exception in command {ctx.command}, guild: {ctx.guild.name}, id={ctx.guild.id}:')
                print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)  

    def setup(self):
        for i in Path('bot/cogs/').glob('*.py'):
            self.load_extension(f'cogs.{i.stem}')

    def run(self):
        self.setup()
        super().run(os.getenv('TOKEN'), reconnect=True)

    async def on_ready(self):
        # Disable Discord.py logging as it's not needed afterwards.
        discord_logger = logging.getLogger('discord')
        discord_logger.setLevel(logging.CRITICAL)

        DiscordComponents(self)
        await self.change_presence(activity=Game(name=f'music | {BASE_PREFIX}help'))

        self._logger.info(f'The bot itself has been successfully launched in approximately {round(perf_counter() - self._start_time, 2)}s')
        delattr(self, '_start_time')

    async def close(self):
        self._logger.info('The bot is being shut down...')
        await super().close()


bot = Bot(db.get_prefix)

data_processor = DataProcessor(bot)
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
