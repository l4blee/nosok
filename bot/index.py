import logging
import os

from dotenv import load_dotenv

from core import bot, data_processor

load_dotenv('bot/.env')

os.makedirs('bot/data', exist_ok=True)
os.makedirs('bot/queues', exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%y.%b.%Y %H:%M:%S')

data_processor.start()
bot.run()

data_processor.close()
