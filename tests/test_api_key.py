import requests

api_key = "sk-H3C2OYsiNnmQEUt0T0LcHKHeiniCC58062ED8399011F1A0B09AB88C137388"

url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "qwen-turbo",
    "messages": [{"role": "user", "content": "你好"}]
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
