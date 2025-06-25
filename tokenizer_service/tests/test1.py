# test_api_requests.py

import requests

# 公用服务地址（根据实际启动 IP/端口调整）
BASE_URL = "http://10.180.116.2:15000"

def test_count_text_simple():
    """
    测试 /Qwen2Tokenizer_count_text/：普通文本计数正确返回，并打印详细信息。
    """
    payload = {"text": "你好，Qwen！"}
    url = f"{BASE_URL}/Qwen2Tokenizer_count_text/"
    r = requests.post(url, json=payload)

    # 打印必要信息
    print("\n[TEST] test_count_text_simple")
    print("URL:", url)
    print("Payload:", payload)
    print("Status code:", r.status_code)
    print("Response JSON:", r.json())

    assert r.status_code == 200, f"Unexpected status: {r.status_code}"
    data = r.json()
    assert "token_count" in data
    assert isinstance(data["token_count"], int) and data["token_count"] > 0


def test_count_text_empty():
    """
    测试 空文本 输入，返回不低于 0 的 token_count，并打印详细信息。
    """
    payload = {"text": ""}
    url = f"{BASE_URL}/Qwen2Tokenizer_count_text/"
    r = requests.post(url, json=payload)

    # 打印必要信息
    print("\n[TEST] test_count_text_empty")
    print("URL:", url)
    print("Payload:", payload)
    print("Status code:", r.status_code)
    print("Response JSON:", r.json())

    assert r.status_code == 200, f"Unexpected status: {r.status_code}"
    count = r.json().get("token_count")
    assert isinstance(count, int) and count >= 0


def test_count_chat_simple():
    """
    测试 /Qwen2Tokenizer_count_chat/：单条消息场景，返回有效 token_count，并打印详细信息。
    """
    payload = {
        "messages": [
            {"role": "user", "content": "你好，Qwen！"}
        ]
    }
    url = f"{BASE_URL}/Qwen2Tokenizer_count_chat/"
    r = requests.post(url, json=payload)

    # 打印必要信息
    print("\n[TEST] test_count_chat_simple")
    print("URL:", url)
    print("Payload:", payload)
    print("Status code:", r.status_code)
    print("Response JSON:", r.json())

    assert r.status_code == 200, f"Unexpected status: {r.status_code}"
    data = r.json()
    assert "token_count" in data
    assert isinstance(data["token_count"], int) and data["token_count"] > 0


def test_count_chat_multiple():
    """
    测试 多条消息 场景，确保合并后 token_count 增加，并打印详细信息。
    """
    payload = {
        "messages": [
            {"role": "user", "content": "请介绍一下你自己。"},
            {"role": "assistant", "content": "我是基于 Transformer 的模型。"},
            {"role": "user", "content": "再算一下 token 数？"}
        ]
    }
    url = f"{BASE_URL}/Qwen2Tokenizer_count_chat/"
    r = requests.post(url, json=payload)

    # 打印必要信息
    print("\n[TEST] test_count_chat_multiple")
    print("URL:", url)
    print("Payload:", payload)
    print("Status code:", r.status_code)
    print("Response JSON:", r.json())

    assert r.status_code == 200, f"Unexpected status: {r.status_code}"
    count = r.json().get("token_count")
    assert isinstance(count, int) and count > 0

if __name__ == "__main__":
    test_count_text_simple()
    test_count_chat_simple()
    test_count_chat_multiple()
    test_count_text_empty()