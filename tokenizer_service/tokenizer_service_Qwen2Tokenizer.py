import os
# 使用 Hugging Face 镜像源
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer



app = FastAPI()

# 要统计的模型名称
MODEL_NAME = "Qwen/QwQ-32B-AWQ"

# 加载 tokenizer，强制 Python 版以保证兼容性
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    use_fast=False,
    trust_remote_code=False
)
# 覆盖最大长度，使其与模型配置一致
tokenizer.model_max_length = 131072
tokenizer.padding_side = "right"


# 普通文本计数的数据模型
class TextItem(BaseModel):
    text: str


# 聊天消息的数据模型
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatItems(BaseModel):
    messages: List[ChatMessage]


@app.post("/Qwen2Tokenizer_count_text/")
async def count_text(item: TextItem):
    """
    计算普通文本的 token 数
    """
    token_ids = tokenizer.encode(
        item.text,
        add_special_tokens=True,
        truncation=True,
        max_length=tokenizer.model_max_length
    )
    return {"token_count": len(token_ids)}


@app.post("/Qwen2Tokenizer_count_chat/")
async def count_chat(items: ChatItems):
    """
    计算聊天场景下按 ChatML 模板合并后的 token 数，
    并包含生成提示（assistant 接下来输出前的标记）。
    """
    # 1) 拼接成符合 ChatML 规范的字符串，自动包含 <|im_start|>/<|im_end|> 等标记
    chat_str = tokenizer.apply_chat_template(
        [msg.dict() for msg in items.messages],
        tokenize=False,
        add_generation_prompt=True   # 包含生成提示
    )

    # 2) 对拼好的字符串做分词，不重复添加 BOS/EOS 等特殊 token
    inputs = tokenizer(
        chat_str,
        return_tensors="pt",
        add_special_tokens=False
    )

    # 3) 读取 token 数
    count = inputs["input_ids"].shape[-1]
    return {"token_count": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=15000)