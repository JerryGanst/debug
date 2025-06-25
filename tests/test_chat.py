import requests

url = "http://127.0.0.1:10000/chat"
headers = {"Content-Type": "application/json"}
payload = {
    "messages": [
        {"role": "user", "content": "怎么请假？"},  # 修改问题内容
        # {"role": "assistant", "content": "您需要先登录HR系统..."}  # 多轮对话时添加历史
    ],
    "user_id": "12345",
    "stream": False,
    "model": "qwen-qwq-reasoning"
}

if __name__ == "__main__":
    response = requests.post(url, json=payload, headers=headers, stream=True)
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
    print(response)