import requests
import time
import os

while True:
    print('Trying to connect')
    try:
        requests.get(f"http://0.0.0.0:{os.environ.get('PORT', 5000)}",
                     headers={})
    except requests.exceptions.ConnectionError:
        print('connection refused')
    print('Now sleeping')
    time.sleep(60)
