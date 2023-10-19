import requests

url = 'http://localhost:8000/questions/'
data = {"questions_num": 5}
response = requests.post(url, json=data)
