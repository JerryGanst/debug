from pydantic import BaseModel
from typing import List

from agents.ask_agent import ask_local_agent
from configs.load import load_config
from models.query import QueryRequest
from configs.load import ModelRouter

class SummaryResponse(BaseModel):
    summary: str  # 主要摘要
    key_points: List[str]  # 重点信息


def summarize(request: QueryRequest):
    config = load_config()
    router = ModelRouter(config)
    text_to_summarize = request.question
    prompt = '''
    请你对以下文本进行结构化总结，具体要求如下：

    1. 输出一个简洁、清晰的摘要，字数控制在100字以内，概括文本的核心内容。
    2. 提炼并以条目形式列出文本中的关键要点，每个要点不超过30字，条目数量不超过5个。

    待总结的文本如下：
    {text}

    请以如下JSON格式输出总结结果：
    {{
        "summary": "主要摘要文本",
        "key_points": ["关键要点1", "关键要点2", "关键要点3"]
    }}

    不需要其他说明。
    '''.format(text=text_to_summarize)

    openai_api_key = router.get_model_config("summarization").get("key", "SOME_KEY")
    openai_api_base = router.get_model_config("summarization").get("endpoint")
    temperature = router.get_model_config("summarization").get("temperature", 0.0)
    thinking = router.get_model_config("summarization").get("thinking")

    return ask_local_agent(prompt, response_type=SummaryResponse, api_key=openai_api_key,
                           api_base=openai_api_base, temperature=temperature, thinking = thinking).get("answer")
