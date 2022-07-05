import os
import logging

from core import bot

# Logging settings stuff
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')


# Creating dirs for futher usage. *Required
os.makedirs('bot/data', exist_ok=True)
os.makedirs('bot/queues', exist_ok=True)

bot.run(
    os.getenv('TOKEN'),
    log_level=logging.CRITICAL
)
