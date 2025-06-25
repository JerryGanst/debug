from typing import List, Dict
import numpy as np
import requests
from pydantic import BaseModel, Field
from fastapi import HTTPException
import logging
from configs.load import load_config
config = load_config()


# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 请求模型
class SimilarityRequest(BaseModel):
    str1: str = Field(..., description="第一个文本字符串")
    str2: str = Field(..., description="第二个文本字符串")


# 响应模型
class SimilarityResponse(BaseModel):
    score: float = Field(..., description="两个文本的相似度分数，范围0-1")


# 计算余弦相似度
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算两个向量的余弦相似度"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)

    # 避免除零错误
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


# 获取文本的embedding向量
def get_embedding(text: str) -> List[float]:
    """调用embedding服务获取文本的向量表示"""
    embedding_endpoint = config.get("context_retrieval").get("embedding_endpoint")

    try:
        response = requests.post(embedding_endpoint, params={"text": text})
        response.raise_for_status()
        return response.json().get('embedding')
    except Exception as e:
        logger.error(f"获取embedding失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取embedding失败: {str(e)}")