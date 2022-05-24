import time
from urllib.request import urlopen
from urllib.error import HTTPError
import os

url = os.environ.get('app_url')

while True:
    try:
        print(f'accessing {url}')
        res = urlopen(url)
    except HTTPError:
        print('Request denied...')
    finally:
        print('Requested successfully')
        time.sleep(600)
