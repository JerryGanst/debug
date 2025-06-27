import json
import os
from openai import OpenAI

from agents.ask_agent import ask_local_agent
from models.query import OptimizedQuestion
from domains.context import DomainContext


def optimize_question(user_question: str, question_category: int, config: dict):
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    # 加载当前领域的问题优化提示词模板
    try:
        prompt_template = domain_config.get_prompt_template("question_optimization")
        # 填充用户问题变量
        prompt = prompt_template.format(user_question=user_question)
    except Exception as e:
        # 如果加载或格式化模板出错，使用通用备选方案
        prompt = f"""
            优化用户问题以便更好地检索相关信息。

            用户问题: {user_question}
            
            返回JSON: 
            {{
              "optimized_question": "改写后的问题",
              "info_to_collect": ["信息点1", "信息点2"]
            }}
        """

    openai_api_key = config.get("key", "SOME_KEY")
    openai_api_base = config.get("endpoint")
    temperature = config.get("temperature", 0.0)
    thinking = config.get("thinking")

    return ask_local_agent(prompt, response_type=OptimizedQuestion, api_key=openai_api_key, api_base=openai_api_base, temperature=temperature, thinking = thinking)


if __name__ == "__main__":
    pass
    # x = optimize_question("服务器怎么申请？", 1, {"endpoint": "http://172.16.10.2:6379/v1"})
    # print(x)
    # print(OptimizedQuestion.model_json_schema())