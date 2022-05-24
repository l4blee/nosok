import time
import urllib
import os

url = os.environ.get('app_url')

while True:
    try:
        print(f'accessing {url}')
        res = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        print('Request denied...')
    finally:
        time.sleep(600)
