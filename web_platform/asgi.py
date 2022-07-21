import os

from app import app

if __name__ == '__main__':
    app.run('0.0.0.0', os.getenv('PORT'), workers=1)
