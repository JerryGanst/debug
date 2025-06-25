import requests

url = "http://localhost:8000/embed/"


if __name__ == "__main__":
    for i in range(100):
        params = {"text": "这是一个测试文本Hello"*20 + "salt" * i}
        response = requests.post(url, params=params)
        embedding_result = response.json().get('embedding')
        print(len(embedding_result))