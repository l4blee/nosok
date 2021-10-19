import logging
import os
from importlib import import_module
from pathlib import Path

import sqlalchemy as sa
from discord.ext import commands
from discord_components.client import DiscordComponents
from youtube_dl.utils import std_headers

from base import Base
from handlers import YDLHandler, YTAPIHandler

# Creating YouTube API handler
google_api_token = os.environ.get('GOOGLE_API_TOKEN')
ytapi_handler = YTAPIHandler(google_api_token)

# Creating YouTubeDL handler
std_headers['Aser-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/51.0.2704.103 Safari/537.36'
ydl_handler = YDLHandler({
    'simulate': True,
    'quiet': True,
    'format': 'bestaudio/best'
})


class Config(Base):
    __tablename__ = 'config'

    guild_id = sa.Column('guild_id', sa.BigInteger, unique=True, primary_key=True)
    prefix = sa.Column('prefix', sa.String, server_default='!')


class MusicBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, case_insensetive=True)
        self._logger = None

    def setup(self):
        for cls in [
            import_module(f'cogs.{i.stem}').__dict__[i.stem.title()]
            for i in Path('./cogs/').glob('*.py')
        ]:
            self.add_cog(eval('cls()'))

    def run(self):
        self.setup()
        TOKEN = os.getenv('TOKEN')
        super().run(TOKEN, reconnect=True)
    
    async def on_ready(self):
        DiscordComponents(self)

        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                            datefmt='%y.%b.%Y %H:%M:%S')
        self._logger = logging.getLogger('index')
        self._logger.warning('Bot has been successfully launched')

    async def close(self):
        self._logger.warning('The bot has been shut down...')
        await super().close()
