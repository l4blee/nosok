from os import getenv

from orm.base import BaseModel
from peewee import BigIntegerField, CharField


class GuildConfig(BaseModel):
    guild_id = BigIntegerField(unique=True, primary_key=True)
    prefix = CharField(default=getenv('BASE_PREFIX'))

    class Meta:
        db_table = 'config'
