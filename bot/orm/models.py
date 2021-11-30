from os import getenv

from dotenv import load_dotenv
from orm.base import BaseModel
from peewee import BigIntegerField, CharField

load_dotenv('bot/.env')


class GuildConfig(BaseModel):
    guild_id = BigIntegerField(unique=True, primary_key=True)
    prefix = CharField(default=getenv('BASE_PREFIX'))

    class Meta:
        db_table = 'config'
