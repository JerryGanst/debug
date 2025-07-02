from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import os
import logging
from routes.chat import ChatRequest, chat_stream, chat_non_stream
from models.query import QueryRequest, WholeProcessRecorder, RecordQueryParams
from routes.summarization import SummaryResponse, summarize
from routes.translation import translate, TranslationResponse, TranslationRequest
from routes.prompt_filler import prompt_filler, AgentConfig
from stream_processor import stream_response
from routes.similarity import SimilarityRequest, SimilarityResponse, get_embedding, cosine_similarity
from domains.context import DomainContext
from configs.load_env import settings
from tokenizer_service import TokenCounter
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from mongodb.ops.object_op import get_objects_by_conditions
from routes.personal_knowledge_base.rag_pipeline import router as personal_rag

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 从环境变量获取领域名称
domain_name = os.environ.get('DOMAIN_NAME')
if not domain_name:
    logger.warning("未设置DOMAIN_NAME环境变量")

# 加载.env的环境变量
logger.info(f"尝试加载.env的环境变量")
if settings.domain_name:
    domain_name = settings.domain_name
    logger.info(f"成功加载.env文件中的DOMAIN_NAME环境变量: {domain_name}")
else:
    logger.warning("未设置.env文件中的DOMAIN_NAME环境变量，请在.env文件中设置DOMAIN_NAME环境变量")

# 应用启动时一次性初始化领域配置，明确传入环境变量
domain_context = DomainContext.initialize(domain_name)

app = FastAPI()

# 创建token计数器实例
token_counter = TokenCounter()

app.include_router(personal_rag)

# Define request model

# Chat 接口
@app.post("/chat")
async def process_chat(request: ChatRequest):
    # 只检查最后一条消息的token数
    if request.messages:
        # 将文件信息加入该条消息里
        if request.file is not None:  # 有文件内容才处理
            # 拼接文件
            formatted_files = "\n\n".join(
                f"文件{i + 1}：\n{content}" for i, content in enumerate(request.file)
            )
            # 将文件加入content
            request.messages[-1].content += (
                "\n\n#####用户提供的文件内容开始#####\n\n"
                f"{formatted_files}\n\n"
                "#####用户提供的文件内容结束#####\n\n"
            )
        last_message = request.messages[-1].dict()
        token_count = token_counter.count_text(last_message["content"])
        if token_count > token_counter.token_limit:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "输入token超过限制",
                    "token_count": token_count,
                    "token_limit": token_counter.token_limit
                }
            )
    
    if request.stream:
        return StreamingResponse(
            chat_stream(request),
            media_type="text/event-stream"
        )
    else:
        return await chat_non_stream(request)

# prompt_filler接口
@app.post("/prompt_fill")
async def process_prompt(config:AgentConfig):
    # 检查输入提示词的token数
    token_count = token_counter.count_text(config.agent_description)
    if token_count > token_counter.token_limit:
        return JSONResponse(
            status_code=400,
            content={
                "error": "输入token超过限制",
                "token_count": token_count,
                "token_limit": token_counter.token_limit
            }
        )
    if config.agent_description == '':
        config = AgentConfig(agent_name = config.agent_name, agent_role = config.agent_role, agent_tone = config.agent_tone)
    if config.agent_tone == '':
        config = AgentConfig(agent_name = config.agent_name, agent_role = config.agent_role, agent_description = config.agent_description)
    return prompt_filler(config)

@app.post("/query")
async def process_query(request: QueryRequest):
    # 检查输入question的token数
    token_count = token_counter.count_text(request.question)
    if token_count > token_counter.token_limit:
        return JSONResponse(
            status_code=400,
            content={
                "error": "输入token超过限制",
                "token_count": token_count,
                "token_limit": token_counter.token_limit
            }
        )
    
    return StreamingResponse(stream_response(request), media_type="text/event-stream")


@app.post("/summarize", response_model=SummaryResponse, response_class=JSONResponse)
async def process_summary(request: QueryRequest):
    # 检查输入question的token数
    token_count = token_counter.count_text(request.question)
    if token_count > token_counter.token_limit:
        return JSONResponse(
            status_code=400,
            content={
                "error": "输入token超过限制",
                "token_count": token_count,
                "token_limit": token_counter.token_limit
            }
        )
    
    return summarize(request)


@app.post("/translate")
async def process_translation(request: TranslationRequest):
    SUPPORTED_LANGUAGES = ["中文", "英文", "越南语", "西班牙语"]

    if request.target_language not in SUPPORTED_LANGUAGES:
        error_message = f"不支持的语种: {request.target_language}。支持的语种有: {', '.join(SUPPORTED_LANGUAGES)}"
        return JSONResponse(status_code=400, content={"error": error_message})

    token_count = token_counter.count_text(request.source_text)
    if token_count > token_counter.token_limit:
        return JSONResponse(
            status_code=400,
            content={
                "error": "输入token超过限制",
                "token_count": token_count,
                "token_limit": token_counter.token_limit
            }
        )

    return StreamingResponse(translate(request), media_type="text/event-stream")


@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """计算两个文本字符串的相似度"""

    # 获取两个文本的embedding
    embedding1 = get_embedding(request.str1)
    embedding2 = get_embedding(request.str2)

    # 计算相似度
    similarity_score = cosine_similarity(embedding1, embedding2)

    return SimilarityResponse(score=similarity_score)



# 兜底防错
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误，请稍后再试"},
    )

@app.get("/test_error")
def test_error_endpoint():
    """
    这个接口直接抛出一个 HTTPException(500),
    用于测试客户端是否能够收到异常。
    """
    raise HTTPException(
        status_code=500,
        detail="这是用于测试抛出异常的例子"
    )

# 显示当前活动领域信息
@app.get("/domain-info")
def domain_info():
    """返回当前活动的领域信息"""
    domain_config = DomainContext.get_config()
    return {
        "domain_name": domain_config.DOMAIN_NAME,
        "doc_type": domain_config.DOMAIN_DOC_TYPE,
        "topics": domain_config.DOMAIN_TOPICS,
    }


# 添加token计数测试接口
@app.post("/count-tokens")
async def count_tokens(request: dict):
    """
    测试token计数功能
    
    请求体格式:
    {
        "text": "要计数的文本内容" 
    }
    或
    {
        "messages": [
            {"role": "user", "content": "用户消息"},
            {"role": "assistant", "content": "助手回复"}
        ]
    }
    """
    if "text" in request:
        token_count = token_counter.count_text(request["text"])
        return {
            "token_count": token_count,
            "character_count": len(request["text"]),
            "token_limit": token_counter.token_limit
        }
    elif "messages" in request:
        token_count = token_counter.count_chat(request["messages"])
        char_count = sum(len(msg.get("content", "")) for msg in request["messages"])
        return {
            "token_count": token_count,
            "character_count": char_count,
            "token_limit": token_counter.token_limit
        }
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "请求格式错误，应包含'text'或'messages'字段"}
        )



@app.post("/get_records")
async def get_whole_process_records(
    request: RecordQueryParams
):
    """
    查询whole_process_records，按start_time时间范围过滤，返回所有字段并加domains字段
    """
    conditions = {
        "start_time": {
            "$gte": request.start_time,
            "$lte": request.end_time
        }
    }
    error, records = get_objects_by_conditions(conditions, WholeProcessRecorder, "whole_process_records")
    if error:
        return {"error": error}
    result = []
    for r in records:
        d = r.model_dump()
        d["domain"] = settings.domain_name
        result.append(d)
    return result


# Run using: uvicorn main:app --reload
