from logging import basicConfig, INFO
from os import makedirs, getenv

# Lading env vars if needed
if getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('bot/.env')

# Logging settings stuff
basicConfig(level=INFO,
            format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
            datefmt='%d.%b.%Y %H:%M:%S')

from core import data_processor, event_handler, bot

# Creating dirs for futher usage. *Required
makedirs('bot/data', exist_ok=True)
makedirs('bot/queues', exist_ok=True)

# Starting all the necessary stuff
data_processor.start()
event_handler.start()
bot.run()  # And the bot itself

# Proper closing after all
data_processor.close()
event_handler.close()
