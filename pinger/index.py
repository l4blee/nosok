import requests
import time

while True:
    requests.get('http://localhost:5000')
    time.sleep(60)
