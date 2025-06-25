import json
import re

from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from models.query import ReasoningJsonSchemaWrapper


def ask_local_agent(
    prompt: str,
    response_type: type[BaseModel],
    api_key="SOME_KEY",
    api_base="",
    temperature=0.0,
    max_tokens=8192
):
    """
    prompt: 要给大模型的提示
    response_type: 期望返回的 Pydantic 模型类 (BaseModel 的子类)
    """
    client = OpenAI(api_key=api_key, base_url=api_base)
    models = client.models.list()
    model = models.data[0].id
    print(f"model: {model}, prompt-length: {len(prompt)}")

    final_note = "\n\n#####最后提醒#####\n\n**请避免重复内容，不要连续输出空格，相同字符，或重复内容块**\n\n"
    prompt = prompt + final_note
    prompt = re.sub(r'\s+', ' ', prompt).strip()

    # 这里构造要发送给 guided_json 的 JSON Schema
    if "reasoning" in model:
        # 如果模型名里包含 'reasoning'，则包装含 reasoning、answer 的结构
        wrapper = ReasoningJsonSchemaWrapper(reasoning="", answer=response_type)
        response_json = wrapper.create_wrapped_model().model_json_schema()
        # print(response_json)
    else:
        response_json = response_type.model_json_schema()
    print("response_json:")
    print(response_json)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": prompt}],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={
                    "guided_json": response_json,
                    "sampling_parameters": {"repetition_penalty": 1.2}
                },
            )

            raw_content = response.choices[0].message.content
            parsed_result = json.loads(raw_content)
            print(f"第{attempt+1}次请求")
            print("content:")
            print(parsed_result)
            # 如果模型名字包含 "reasoning"，则返回的数据格式中应该具备 "reasoning" 和 "answer"
            if "reasoning" in model:
                validated = wrapper.create_wrapped_model()(**parsed_result)
                return {
                    "reasoning": validated.reasoning,
                    "answer": validated.answer.dict()
                }
            else:
                # 不包含 reasoning 时，只校验 answer
                validated_answer = response_type(**parsed_result)
                return {
                    "reasoning": "",
                    "answer": validated_answer.dict()
                }

        except (json.JSONDecodeError, ValidationError, KeyError, ValueError) as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail="服务器内部错误，请稍后再试"
                ) from e
            # 未到达最大重试次数，继续下一次
            print("请求重试")
            continue
        except Exception as e:
            # 其他未预料到的错误
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail="服务器内部错误，请稍后再试"
                ) from e
            print("请求重试")
            continue
