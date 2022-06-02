web: gunicorn --chdir server --bind 0.0.0.0:$PORT main:app --preload
worker: python pinger/index.py
