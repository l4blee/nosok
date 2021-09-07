import logging
import os
from importlib import import_module
from pathlib import Path

import discord
from discord.ext import commands

import core


def get_prefix(client: commands.Bot, msg: discord.Message) -> str:
    return core.config.get_or_none(guild_id=msg.guild.id) or '!'


bot = commands.Bot(get_prefix)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')
logger = logging.getLogger('index')


@bot.event
async def on_ready():
    logger.info('Bot has been launched successfully')


for cls in [import_module(f'cogs.{i.stem}').__dict__[i.stem.title()]
            for i in Path('./cogs/').glob('*.py')]:
    exec(f'{cls.__name__.lower()} = cls()')
    bot.add_cog(eval(cls.__name__.lower()))


bot.run(os.getenv('TOKEN'))

core.config.save()
logger.info('The bot has been shut down...')
logger.info('#' * 40)
