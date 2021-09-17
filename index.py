import logging
import os
from importlib import import_module
from pathlib import Path

import discord
from discord.ext import commands
import sqlalchemy as sa
from sqlalchemy import orm

import base
import core


Session = orm.sessionmaker(base.engine)


def get_prefix(client: commands.Bot, msg: discord.Message) -> str:
    with Session() as s:
        prefix = s.query(core.Config).filter_by(guild_id=msg.guild.id)
        return prefix


bot = commands.Bot(get_prefix)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')
logger = logging.getLogger('index')


@bot.event
async def on_ready():
    base.Base.metadata.create_all()
    logger.info('Bot has been launched successfully')


for cls in [import_module(f'cogs.{i.stem}').__dict__[i.stem.title()]
            for i in Path('./cogs/').glob('*.py')]:
    exec(f'{cls.__name__.lower()} = cls()')
    bot.add_cog(eval(cls.__name__.lower()))


bot.run(os.getenv('TOKEN'))

logger.info('The bot has been shut down...')
logger.info('#' * 40)
