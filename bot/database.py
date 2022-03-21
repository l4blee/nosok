from logging import getLogger
from os import getenv

from pymongo import MongoClient
from discord.ext.commands import Context
from discord import Message

from base import BASE_PREFIX


class MongoDB:
    """
    Mongo database class, used everywhere to access Mongo.
    No need to make docstrings for every method as names represent the functionality.
    """
    def __init__(self, conn_url):
        self._logger = getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)
        self.connect(conn_url)
    
    def connect(self, conn_url: str):
        self._logger.info('Connecting to MongoDB...')
        self.client = MongoClient(conn_url)

        # Main database
        self.prefixes = self.client.guilds.prefixes
        self.playlists = self.client.guilds.playlists
        self._logger.info('Successfully connected to Mongo, going further.')

    async def get_prefix(self, _, msg: Message) -> str:
        guild_id = msg.guild.id

        guild_record = self.prefixes.find_one({
            'guild_id': guild_id
        })

        if guild_record is None:
            return BASE_PREFIX
        
        return guild_record.get('prefix')
    
    async def set_prefix(self, ctx: Context, new_prefix: str) -> None:
        self.prefixes.replace_one(
            {'guild_id': ctx.guild.id},
            {
                'guild_id': ctx.guild.id,
                'prefix': new_prefix
            },
            upsert=True
        )


# Creaing DB right here to use everywhere without loop imports, issues, etc.
db = MongoDB(
    getenv('DATABASE_URL') % {
        'username': getenv('DB_USERNAME'),
        'password': getenv('DB_PASSWORD')
    }
)