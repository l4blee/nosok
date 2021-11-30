from os import getenv

from dotenv import load_dotenv
from peewee import Model, PostgresqlDatabase

load_dotenv('bot/.env')

_, db_url = getenv('DATABASE_URL').split('//')

user, pass_host, port_db = db_url.split(':')
password, host = pass_host.split('@')
port, database = port_db.split('/')

db = PostgresqlDatabase(
    database=database,
    user=user,
    password=password,
    host=host,
    port=port,
)


class BaseModel(Model):
    class Meta:
        database = db
