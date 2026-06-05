from concurrent.futures import ThreadPoolExecutor
import requests

URL = "http://localhost:8000/api/v1/users/register"
DATA = {"username": "conc_test4", "password": "123", "role": "user"}

def login():
    try:
        response = requests.post(URL, json=DATA)
        print(response.json())
    except Exception as e:
        print(f"请求出错: {e}")

# 并发测试
with ThreadPoolExecutor(max_workers=10) as executor:
    for _ in range(10):
        executor.submit(login)