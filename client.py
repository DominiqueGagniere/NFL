import requests

url = 'http://localhost:5000/ip'
data = 192.168.1.1

response = requests.post(url, json=data)