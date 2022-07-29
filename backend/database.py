import os

from pymongo import MongoClient


class MongoDB:
    def __init__(self, conn_url):
        self._setup(conn_url)

    def _setup(self, conn_url: str):
        self.client = MongoClient(conn_url)
        self.users = self.client.web.users  # Main database


database = MongoDB(
    os.getenv('DATABASE_URL').format(
        os.getenv('DB_USERNAME'),
        os.getenv('DB_PASSWORD')
    )
)
