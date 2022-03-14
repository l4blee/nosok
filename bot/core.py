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

    async def on_command_error(self, ctx: commands.Context, exception):
        if not isinstance(exception, CustomException):
            if isinstance(exception, commands.CommandNotFound):
                await send_embed(ctx,
                                f'Command not found, type in `{ctx.prefix}help` to get the list of all the commands available.', 
                                ERROR_COLOR)
            else:
                await send_embed(ctx,
                             'An error occured during handling this command, please try again later.', 
                             ERROR_COLOR)

        self._logger.warning('Ignoring exception in command {}:'.format(ctx.command))
        print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)  

    def setup(self):
        # db.create_tables([GuildConfig])

        for cls in [
            import_module(f'cogs.{i.stem}').__dict__[i.stem.title()]
            for i in Path('./bot/cogs/').glob('*.py')
        ]:
            self.add_cog(eval('cls()'))

    def run(self):
        self.setup()
        TOKEN = os.getenv('TOKEN')
        super().run(TOKEN, reconnect=True)

    async def on_ready(self):
        Queue = import_module('cogs.music').__dict__['Queue']
        self.get_cog('Music')._queues = {i.id: Queue(i.id) for i in self.guilds}
        del Queue

        DiscordComponents(self)

        self._logger.info(f'The bot has been successfully launched in approximately {round(perf_counter() - self._start_time, 2)}s')
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
