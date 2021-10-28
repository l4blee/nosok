import requests
import time
import os

while True:
    requests.get(f"http://localhost:{os.environ.get('PORT', 5000)}")
    time.sleep(60)
