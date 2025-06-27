import json
import re

from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel, ValidationError


def ask_local_agent(
    prompt: str,
    response_type: type[BaseModel],
    api_key="SOME_KEY",
    api_base="",
    temperature=0.0,
    thinking=False,
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
    prompt = re.sub(r'\s+', ' ', prompt + final_note).strip()

    # Build JSON schema from the response model, activate only ready to fully switch to qwen3
    response_json = response_type.model_json_schema()

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
                    "sampling_parameters": {"repetition_penalty": 1.2},
                    "chat_template_kwargs": {"enable_thinking": thinking},
                },
            )

            msg = response.choices[0].message
            raw_content = msg.content
            raw_reasoning_content = msg.reasoning_content

            print(f"第{attempt + 1}次请求")
            print("RAW content:", raw_content)
            print("RAW reasoning_content:", raw_reasoning_content)

            parsed_result = json.loads(raw_content)
            validated_answer = response_type.model_validate(parsed_result)

            return {
                "reasoning": raw_reasoning_content if thinking else "",
                "answer": validated_answer.model_dump()
            }

        except (json.JSONDecodeError, ValidationError, KeyError, ValueError) as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail="服务器内部错误，请稍后再试"
                ) from e
            print("请求重试 due to known error:", repr(e))
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail="服务器内部错误，请稍后再试"
                ) from e
            print("请求重试 due to unknown error:", repr(e))
            continue
