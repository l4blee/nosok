from base import Base
from core import bot


Base.metadata.create_all()
bot.run()
