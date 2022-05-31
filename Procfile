web: gunicorn --chdir server --bind 0.0.0.0:$PORT --access-logfile - main:app --preload
worker: python pinger/index.py
