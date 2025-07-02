import os
from agents.ask_agent import ask_local_agent
from models.query import QuestionClassification
from domains.context import DomainContext


def classify_question(user_question, config: dict):
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    # 加载当前领域的问题分类提示词模板
    try:
        prompt_template = domain_config.get_prompt_template("question_classification")
        # 填充用户问题变量
        prompt = prompt_template.format(user_question=user_question)
    except Exception as e:
        # 如果加载或格式化模板出错，使用通用备选方案
        prompt = f"""
            分析用户问题并归类。
            
            用户问题: {user_question}
            
            返回JSON: {{"category": 1, "reason": "分类原因"}}
        """
    
    openai_api_key = config.get("key", "SOME_KEY")
    openai_api_base = config.get("endpoint")
    temperature = config.get("temperature", 0.0)
    thinking = config.get("thinking")

    return ask_local_agent(prompt, response_type=QuestionClassification, api_key=openai_api_key,
                           api_base=openai_api_base, temperature=temperature, thinking = thinking)