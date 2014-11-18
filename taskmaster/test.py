import requests
from requests_futures.sessions import FuturesSession

requests.post('http://127.0.0.1:8888/process/1/start')

session = FuturesSession()
future = session.get('http://127.0.0.1:8888/logs/streaming/1')

result = future.result()
print(result.content)