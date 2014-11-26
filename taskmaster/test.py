import requests
from requests_futures.sessions import FuturesSession
import time

session = FuturesSession()
future = session.get('http://127.0.0.1:8888/process_status/0.0')
result = future.result()
print('Status: {}'.format(result.json()))

requests.post('http://127.0.0.1:8888/process/2/start')