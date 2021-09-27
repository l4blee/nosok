import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from base import Base, engine
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
    yt_handler = YDLHandler({
        'quiet': True,
        'format': 'bestaudio/best'
    })

Session = sessionmaker(bind=engine)
