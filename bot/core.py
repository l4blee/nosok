import os
import sys
from time import perf_counter
from importlib import import_module
from logging import getLogger
from pathlib import Path
from traceback import print_exception

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
        self._logger = getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)

    async def on_message(self, message):
        '''if not message.author.bot:
            await event_handler.on_message(message)'''
        # TODO: use event_handler to make the bot leave a voice channel with a message accepted

        await super().on_message(message)

    async def on_command_error(self, ctx: commands.Context, exception):
        if isinstance(exception, CustomException):
            await send_embed(
                ctx=ctx, 
                description=exception.description, 
                color=exception.type_.value)
            return
        else:
            if isinstance(exception, commands.CommandNotFound):
                await send_embed(ctx,
                                f'Command not found, type in `{ctx.prefix}help` to get the list of all the commands available.', 
                                ERROR_COLOR)
                return
            elif isinstance(exception, commands.MissingRequiredArgument):
                await send_embed(ctx,
                                f'Please provide {exception.param.name}. '
                                f'Type `{ctx.prefix}help {ctx.invoked_with}` to get help.', 
                                ERROR_COLOR)
                return
            else:
                await send_embed(ctx,
                             'An error occured during handling this command, please try again later.', 
                             ERROR_COLOR)
                return
            

        self._logger.warning('Ignoring exception in command {}:'.format(ctx.command))
        print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)  

    def setup(self):
        for i in Path('bot/cogs/').glob('*.py'):
            self.load_extension(f'cogs.{i.stem}')

    def run(self):
        self.setup()
        super().run(os.getenv('TOKEN'), reconnect=True)

    async def on_ready(self):
        DiscordComponents(self)

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
    'format': 'bestaudio'
})
