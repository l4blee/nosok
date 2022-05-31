web: gunicorn --chdir server --bind localhost:$PORT --access-logfile - main:app
worker: python pinger/index.py
