import logging
import os

if os.getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('bot/.env')

from core import bot, data_processor, event_handler

os.makedirs('bot/data', exist_ok=True)
os.makedirs('bot/queues', exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

data_processor.start()
event_handler.start()
bot.run()

data_processor.close()
event_handler.close()
