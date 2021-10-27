import logging
from base import DBBase
from core import bot, con_handler

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')

DBBase.metadata.create_all()
con_handler.run()
bot.run(con_handler)