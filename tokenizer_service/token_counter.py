import requests
from typing import List, Dict, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel, parse_obj_as

from configs.load import load_config


class ChatMessage(BaseModel):
    role: str
    content: str


class TokenCounter:
    def __init__(self):
        config = load_config()
        self.tokenizer_endpoint = config.get("tokenizer_service", {}).get("tokenizer_endpoint", "")
        self.token_limit = 20000  # 设置token限制

    def count_text(self, text: str) -> int:
        """
        计算纯文本的token数量
        
        Args:
            text: 需要计算token的文本
            
        Returns:
            int: token数量，如果服务不可用则返回字符数
        """
        if not text:
            return 0
            
        try:
            response = requests.post(
                f"{self.tokenizer_endpoint}/Qwen2Tokenizer_count_text/",
                json={"text": text},
                timeout=3  # 添加超时设置
            )
            response.raise_for_status()
            return response.json().get("token_count", 0)
        except Exception as e:
            print(f"Token计数失败，使用字符长度作为近似值: {str(e)}")
            # 如果token计数服务不可用，使用字符数作为近似值
            return len(text)

    def count_chat(self, messages: List[Dict[str, str]]) -> int:
        """
        计算聊天消息的token数量
        
        Args:
            messages: 聊天消息列表，每条消息包含role和content
            
        Returns:
            int: token数量，如果服务不可用则返回字符总数
        """
        if not messages:
            return 0
            
        try:
            # 转换成正确的格式
            chat_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in messages]
            response = requests.post(
                f"{self.tokenizer_endpoint}/Qwen2Tokenizer_count_chat/",
                json={"messages": [msg.dict() for msg in chat_messages]},
                timeout=3  # 添加超时设置
            )
            response.raise_for_status()
            return response.json().get("token_count", 0)
        except Exception as e:
            print(f"Chat Token计数失败，使用字符长度作为近似值: {str(e)}")
            # 如果token计数服务不可用，使用字符总数作为近似值
            return sum(len(msg.get("content", "")) for msg in messages)

    def check_text_token_limit(self, text: str) -> Dict[str, Any]:
        """
        检查文本是否超过token限制
        
        Args:
            text: 需要检查的文本
            
        Returns:
            Dict: 包含token数量和是否超限的信息
            
        Raises:
            HTTPException: 如果token超过限制，抛出400异常
        """
        token_count = self.count_text(text)
        if token_count > self.token_limit:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "输入token超过限制",
                    "token_count": token_count,
                    "token_limit": self.token_limit
                }
            )
        return {"token_count": token_count, "exceeds_limit": False}

    def check_chat_token_limit(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        检查聊天消息是否超过token限制
        
        Args:
            messages: 聊天消息列表
            
        Returns:
            Dict: 包含token数量和是否超限的信息
            
        Raises:
            HTTPException: 如果token超过限制，抛出400异常
        """
        token_count = self.count_chat(messages)
        if token_count > self.token_limit:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "输入token超过限制",
                    "token_count": token_count,
                    "token_limit": self.token_limit
                }
            )
        return {"token_count": token_count, "exceeds_limit": False} 