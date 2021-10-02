import logging
import os
from importlib import import_module
from pathlib import Path

from base import Base
from core import bot

Base.metadata.create_all()
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')
logger = logging.getLogger('index')


@bot.event
async def on_ready():
    logger.warning('Bot has been successfully launched')


for cls in [import_module(f'cogs.{i.stem}').__dict__[i.stem.title()] for i in Path('./cogs/').glob('*.py')]:
    exec(f'{cls.__name__.lower()} = cls()')
    bot.add_cog(eval(cls.__name__.lower()))


bot.run(os.getenv('TOKEN'))
logger.info('The bot has been shut down...')
