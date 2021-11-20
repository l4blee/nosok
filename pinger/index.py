import requests
import time

while True:
    try:
        res = requests.get('https://nosok.herokuapp.com')
    except requests.exceptions.RequestException:
        print('Request denied...')
    finally:
        time.sleep(600)
