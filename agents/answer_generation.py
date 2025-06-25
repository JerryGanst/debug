from typing import List
import os

from agents.ask_agent import ask_local_agent
from models.query import LLMAnswer, ContextSource, Answer
from domains.context import DomainContext


def generate_answer(optimized_question: str, contexts: List[ContextSource], question_category: int,
                    config: dict):
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    # 创建上下文列表用于格式化模板
    context_list = []
    for i, ctx in enumerate(contexts):
        context_text = f"来源{i + 1}：《{ctx.document_title}》"
        if ctx.page is not None:
            context_text += f"（第{ctx.page}页）"
        context_text += f"\n{ctx.text}"
        context_list.append(context_text)

    all_contexts = "\n\n".join(context_list)
    
    # 加载当前领域的答案生成提示词模板
    try:
        prompt_template = domain_config.get_prompt_template("answer_generation")
        # 填充变量
        prompt = prompt_template.format(
            optimized_question=optimized_question,
            all_contexts=all_contexts
        )
    except Exception as e:
        # 如果加载或格式化模板出错，使用通用备选方案
        prompt = f"""
            基于给定的上下文回答用户问题。

            用户问题: {optimized_question}
            
            上下文信息:
            {all_contexts}
            
            返回JSON:
            {{
              "is_question_answered": true或false,
              "answer": "回答内容",
              "context_ids": [使用的上下文编号，从1开始]
            }}
        """

    openai_api_key = config.get("key", "SOME_KEY")
    openai_api_base = config.get("endpoint")
    temperature = config.get("temperature", 0.0)

    parsed_result = ask_local_agent(prompt, response_type=LLMAnswer, api_key=openai_api_key,
                                    api_base=openai_api_base, temperature=temperature)

    # Convert context_ids from 1-based to 0-based for internal use
    parsed_result["answer"]["context_ids"] = [idx - 1 for idx in parsed_result.get("answer").get("context_ids", [])]

    llm_answer = LLMAnswer(**parsed_result.get("answer"))
    final_answer = Answer(is_question_answered=llm_answer.is_question_answered, answer=llm_answer.answer, contexts=[])

    if final_answer.is_question_answered:
        for idx in llm_answer.context_ids:
            if 0 <= idx < len(contexts):
                final_answer.contexts.append(contexts[idx])
    parsed_result["answer"] = final_answer.model_dump()
    return parsed_result


if __name__ == "__main__":
    # Test the function
    test_question = "如何申请一台开发服务器？"
    test_contexts = [
        ContextSource(
            document_id="doc1",
            document_title="IT 设备管理规范",
            page=3,
            text="员工申请开发服务器需填写《服务器申请表》，提交至 IT 部门审批，审批通过后将在 3 个工作日内分配资源。"
        ),
        ContextSource(
            document_id="doc2",
            document_title="技术支持手册",
            page=8,
            text="开发服务器的申请需明确用途（如开发、测试），并由部门负责人签字确认。"
        )
    ]
    test_result = generate_answer(test_question, test_contexts, 1, {"endpoint": "http://172.16.10.2:6379/v1"})
    print(test_result)