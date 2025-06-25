import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import HTTPException
import pytest
import requests
from tokenizer_service.token_counter import TokenCounter


def test_count_text():
    """测试纯文本token计数"""
    counter = TokenCounter()
    token_count = counter.count_text("这是一个测试文本，用于测试token计数功能。")
    assert isinstance(token_count, int)
    assert token_count > 0
    print(f"测试文本的token数量: {token_count}")


def test_count_chat():
    """测试聊天消息token计数"""
    counter = TokenCounter()
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"},
        {"role": "assistant", "content": "我是一个AI助手"}
    ]
    token_count = counter.count_chat(messages)
    assert isinstance(token_count, int)
    assert token_count > 0
    print(f"聊天消息的token数量: {token_count}")


def test_check_text_token_limit_normal():
    """测试正常文本不会超过token限制"""
    counter = TokenCounter()
    result = counter.check_text_token_limit("这是一个简短的测试文本")
    assert result["token_count"] > 0
    assert result["exceeds_limit"] is False
    print(result)


def test_check_text_token_limit_exceed():
    """测试超长文本会引发HTTPException"""
    counter = TokenCounter()
    counter.token_limit = 10  # 临时设置为低值以便测试
    with pytest.raises(HTTPException) as excinfo:
        counter.check_text_token_limit("这是一个超长的测试文本，肯定会超过我们设置的10个token的限制")
    
    assert excinfo.value.status_code == 400
    assert "token_count" in excinfo.value.detail
    assert "token_limit" in excinfo.value.detail
    assert "error" in excinfo.value.detail
    # 打印关键异常信息
    print("\n=== 异常详情 ===")
    print(f"状态码: {excinfo.value.status_code}")
    print(f"错误信息: {excinfo.value.detail['error']}")
    print(f"Token计数: {excinfo.value.detail['token_count']}")
    print(f"限制值: {excinfo.value.detail['token_limit']}")


def test_check_chat_token_limit():
    """测试聊天消息token限制检查"""
    counter = TokenCounter()
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么可以帮助你的？"}
    ]
    result = counter.check_chat_token_limit(messages)
    assert result["token_count"] > 0
    assert result["exceeds_limit"] is False


if __name__ == "__main__":
    print("运行token计数测试...")
    test_count_text()
    test_count_chat()
    test_check_text_token_limit_normal()
    
    try:
        test_check_text_token_limit_exceed()
        print("超限异常测试失败")
    except Exception as e:
        print(f"超限异常测试通过: {e}")
    
    test_check_chat_token_limit()
    print("所有测试完成") 