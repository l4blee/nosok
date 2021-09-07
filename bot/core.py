import os

import peewee

name = os.getenv('db-name')
host = os.getenv('db-host')
port = int(os.getenv('db-port'))
user = os.getenv('db-username')
password = os.getenv('db-password')
db = peewee.MySQLDatabase(name,
                          host=host,
                          port=port,
                          user=user,
                          password=password)


class Config(peewee.Model):
    guild_id = peewee.IntegerField(unique=True)
    prefix = peewee.CharField()

    class Meta:
        database = db


config = Config()
config.create_table()
