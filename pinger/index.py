import requests
import time
import os

url = os.environ.get('app_url')

while True:
    try:
        print(f'accessing {url}')
        res = requests.get(url)
    except requests.exceptions.RequestException:
        print('Request denied...')
    finally:
        time.sleep(600)
