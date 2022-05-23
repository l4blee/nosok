from logging import getLogger
from os import getenv

from pymongo import MongoClient
from discord.ext.commands import Context, Bot, when_mentioned_or
from discord import Message

from base import BASE_PREFIX, BASE_LANGUAGE


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
        self.guilds = self.client.guilds  # Main database
        
        self._logger.info('Successfully connected to Mongo, going further...')

    async def get_prefix(self, bot: Bot, msg: Message) -> str:
        guild_record = self.guilds.configs.find_one({
            'guild_id': msg.guild.id
        })

        if guild_record is None:
            return BASE_PREFIX
        return guild_record.get('prefix', BASE_PREFIX)

    async def get_language(self, ctx: Context) -> str:
        guild_record = self.guilds.configs.find_one({
            'guild_id': ctx.guild.id
        })

        if guild_record is None:
            return BASE_LANGUAGE
        
        return when_mentioned_or(guild_record.get('language', BASE_LANGUAGE))


# Creaing DB client instance right here to use everywhere without loop imports and other issues.
db = MongoDB(
    getenv('DATABASE_URL') % {
        'username': getenv('DB_USERNAME'),
        'password': getenv('DB_PASSWORD')
    }
)
