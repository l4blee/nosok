import os
import logging

if os.getenv('APP_STATUS', 'production') != 'production':
    from dotenv import load_dotenv
    load_dotenv('server/.env')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s:\t%(message)s',
                    datefmt='%d.%b.%Y %H:%M:%S')

if __name__ == '__main__':
    from core import app, load_blueprints
    from handlers import bot_handler

    # bot_handler.launch()
    app.run('0.0.0.0', port=os.getenv('PORT', 5000))