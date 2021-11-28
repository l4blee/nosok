import logging
import os
from importlib import import_module
from pathlib import Path

import sqlalchemy as sa
import discord
from discord.ext import commands
from discord_components.client import DiscordComponents
from youtube_dl.utils import std_headers

from base import DBBase, Session, BASE_PREFIX
from handlers import YDLHandler, EventHandler, DataProcessor, SCHandler

USE_YOUTUBE = False


class Config(DBBase):
    __tablename__ = 'config'

    guild_id = sa.Column('guild_id', sa.BigInteger, unique=True, primary_key=True)
    prefix = sa.Column('prefix', sa.String, server_default='!')


class MusicBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, case_insensetive=True)
        self._logger = logging.getLogger('BOT')

    def setup(self):
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
        DiscordComponents(self)
        self._logger.info('Bot has been successfully launched')

    async def close(self):
        self._logger.info('The bot is being shut down...')
        await super().close()


def get_prefix(_, msg: discord.Message) -> str:
    with Session.begin() as s:
        res = s.query(Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


bot = MusicBot(get_prefix)
con_handler = DataProcessor(bot)
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
