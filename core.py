import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands

from base import Base, engine, BASE_PREFIX
from handlers import YDLHandler, YTAPIHandler


use_deprecated = False


class Config(Base):
    __tablename__ = 'config'

    guild_id = sa.Column('guild_id', sa.BigInteger, unique=True, primary_key=True)
    prefix = sa.Column('prefix', sa.String, server_default='!')


if use_deprecated and 'GOOGLE_API_TOKEN' in os.environ.keys():
    google_api_token = os.environ.get('GOOGLE_API_TOKEN')
    yt_handler = YTAPIHandler(google_api_token)
else:
    from youtube_dl.utils import std_headers

    std_headers['Aser-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                'Chrome/51.0.2704.103 Safari/537.36'
    yt_handler = YDLHandler({
        'simulate': True,
        'quiet': True,
        'format': 'bestaudio/best'
    })

Session = sessionmaker(bind=engine)


def get_prefix(client: commands.Bot, msg: discord.Message) -> str:
    with Session.begin() as s:
        res = s.query(Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


bot = commands.Bot(get_prefix, case_insensitive=True)
