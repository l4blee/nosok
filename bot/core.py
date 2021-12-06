import os
from importlib import import_module
from logging import getLogger
from pathlib import Path

from discord.ext import commands
from discord_components.client import DiscordComponents
from youtube_dl.utils import std_headers

from base import BASE_PREFIX
from handlers import YDLHandler, EventHandler, DataProcessor, SCHandler
from orm.base import db
from orm.models import GuildConfig

USE_YOUTUBE = False


class MusicBot(commands.Bot):
    __slots__ = ('_logger')

    def __init__(self, command_prefix):
        super().__init__(command_prefix, case_insensetive=True)
        self._logger = getLogger('BOT')

    def setup(self):
        db.create_tables([GuildConfig])

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

        self._logger.info('Bot has been successfully launched')

    async def close(self):
        self._logger.info('The bot is being shut down...')
        await super().close()


def get_prefix(_, msg) -> str:
    with db.atomic():
        res = GuildConfig.get_or_none(GuildConfig.guild_id == msg.guild.id)
        return res.prefix if res is not None else BASE_PREFIX


bot = MusicBot(get_prefix)
data_processor = DataProcessor(bot)
event_handler = EventHandler(bot)

if USE_YOUTUBE:
    std_headers['Aser-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                'Chrome/51.0.2704.103 Safari/537.36'
    music_handler = YDLHandler({
        'simulate': True,
        'quiet': True,
        'format': 'bestaudio/best'
    })
else:
    music_handler = SCHandler()
