import json
import textwrap
from pydantic import BaseModel
from typing import Dict
from openai import OpenAI
import asyncio

from configs.load import load_config, ModelRouter
from utils.glossary.glossary import glossary_extract

class TranslationResponse(BaseModel):
    translation_result: str  # 翻译结果
    
def translate_stream_response(content: str) -> str:
    # 你可以定义一个简单的 Pydantic 模型用于统一数据格式
    response_data = {"translation_result": content}
    json_str = json.dumps(response_data, ensure_ascii=False)
    return f"data: {json_str}\n\n"


class TranslationRequest(BaseModel):
    user_id: str
    target_language: str
    source_text: str


# 目标语言映射表
LANG_MAP: Dict[str, str] = {
    "中文": "Chinese",
    "英文": "English",
    "越南语": "Vietnamese",
    "西班牙语": "Spanish",
}

async def translate(request: TranslationRequest):
    config = load_config()
    router = ModelRouter(config)
    source_text = request.source_text
    target_language = LANG_MAP.get(request.target_language)

    # 构建翻译提示
    system_prompt = textwrap.dedent(f"""
You are a meticulous technical translator, working for ***Luxshare-ICT***, also know as ***立讯精密***.

──────────────────────────── 1. OUTPUT REQUIREMENT ────────────────────────────
You will receive a text with markdown format, translate only the natural‑language 
content between the tags （***SOURCE_TEXT_BEGIN*** and ***SOURCE_TEXT_END***) 
into **{target_language}** and output it as **valid, neatly formatted Markdown**:
• If the source is tabular (CSV, Excel‑like, HTML table), render a Markdown
  table with the same rows and columns, while translate the natural-language 
  content into **{target_language}**.
• Otherwise, render regular Markdown text (headings, lists, paragraphs, etc.).
• Do not add explanations, metadata, or extra fences—output pure Markdown only.
• Do not output any instruction for you.
• Do not output the tag, only output translation result between tags.
• Always and only translate natural-language content into **{target_language}**

──────────────────────────── 2. MARKDOWN REFERENCE ────────────────────────────
• Table       : | col A | col B | … |           (+ second line of --- separators)
• Headings    : # H1 ‖ ## H2 ‖ ### H3 …
• Lists       : - item  ‖ * item  ‖ 1. item (preserve nesting/indent)
• Code        : ```lang … ``` for blocks; `inline code` for snippets
• Links/Images: [text](url)   ‖   ![alt](url)
• Bold/Italic : **bold**  ‖  *italic*
• Math        : leave anything inside $…$ or $$…$$ untouched
• URLs        : never translate or modify

    """)
    # 3. Assistant prompt（Glossary 部分）
    glossary_text = glossary_extract(source_text)
    assistant_prompt = (
        "Glossary (bidirectional, three‑lang):\n" + "\n".join(f"- {line}" for line in glossary_text.split("\n") if line)
        if glossary_text else
        "Glossary: (no matched terms)"
    )

    # 4. User prompt（包裹原文）
    user_prompt = textwrap.dedent(
        f"""***SOURCE_TEXT_BEGIN***\n{source_text}\n***SOURCE_TEXT_END***"""
    )

    config = router.get_model_config("translation")
    api_key = config.get("key", "SOME_KEY")
    api_base = config.get("endpoint")
    thinking = config.get("thinking", False)
    temperature = config.get("temperature", 0.2)

    # Retry logic
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            client = OpenAI(api_key=api_key, base_url=api_base)
            models = client.models.list()
            model = models.data[0].id

            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "assistant", "content": assistant_prompt},
                          {"role": "user", "content": user_prompt}],
                model=model,
                temperature=temperature,
                stream=True,
                extra_body={
                    "sampling_parameters": {"repetition_penalty": 1.2},
                    "chat_template_kwargs": {"enable_thinking": thinking if thinking is not None else False}
                },
            )

            full_response = ""
            async for chunk in response:
                delta = chunk.choices[0].delta.get("content")
                if delta:
                    full_response += delta
                    yield translate_stream_response(delta)

            # Validate response
            if not full_response.strip():
                yield translate_stream_response("[ERROR] Empty translation result.")
            # 结束时发送特殊事件通知
            yield "data: [DONE]\n\n"
            return
        except Exception as e:
            if attempt == max_retries:
                yield translate_stream_response(f"[ERROR] Translation failed after {max_retries} attempts: {str(e)}")
                yield "data: [DONE]\n\n"
                return
            else:
                await asyncio.sleep(1.5)  # Wait before retrying
                continue