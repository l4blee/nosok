import time
import urllib
import os

url = os.environ.get('app_url')

while True:
    try:
        print(f'accessing {url}')
        res = urllib.request.urlopen(url)
    except Exception:
        print('Request denied...')
    
    time.sleep(600)
