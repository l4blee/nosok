import os
import logging

os.chdir('../')

if os.getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('server/.env')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

from core import app
from handlers import bot_handler

bot_handler.launch()

if __name__ == '__main__':
    app.run('0.0.0.0', port=os.getenv('PORT', 5000))
