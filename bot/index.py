import os
import logging

# Lading env vars if needed
if os.getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('bot/.env')

# Logging settings stuff
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

from core import performance_processor, event_handler, bot

# Creating dirs for futher usage. *Required
os.makedirs('bot/data', exist_ok=True)
os.makedirs('bot/queues', exist_ok=True)

# Starting all the necessary stuff
performance_processor.start()
event_handler.start()
bot.run()  # And the bot itself

# Proper closing after all
performance_processor.close()
event_handler.close()
