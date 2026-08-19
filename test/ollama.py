import requests
import json

url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "llama3:8b",
    "prompt": "用一句话解释什么是机器学习",
    "stream": False
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    print(result['response'])
else:
    print(response.status_code)