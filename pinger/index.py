import requests
import time

while True:
    try:
        res = requests.get('https://nosok.herokuapp.com')
    finally:
        time.sleep(600)
