
import logging
import os
from importlib import import_module
from pathlib import Path

import discord
from discord.ext import commands

import core
from base import Base, BASE_PREFIX

Session = core.Session
<<<<<<< HEAD


def get_prefix(client: commands.Bot, msg: discord.Message) -> str:
    with Session.begin() as s:
        res = s.query(core.Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


=======


def get_prefix(client: commands.Bot, msg: discord.Message) -> str:
    with Session.begin() as s:
        res = s.query(core.Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


>>>>>>> parent of 79cb644 (Rewrite YoutubeHandler to make it work with the `youtube-dl` library, add config.py and utils.py)
bot = commands.Bot(get_prefix)
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
