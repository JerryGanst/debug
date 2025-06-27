from typing import List, Optional

from openai import OpenAI  # 使用异步客户端
from pydantic import BaseModel, Field, ValidationError

from configs.load import load_config,ModelRouter
from models.query import QueryRequest, WholeProcessRecorder
from routes.prompt_filler import AgentConfig
from mongodb.ops.object_op import insert_object


config = load_config()
router = ModelRouter(config)

# 对话消息模型
class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色: system, user 或 assistant")
    content: str = Field(..., description="消息内容")

# 对话请求模型
class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="对话历史消息列表")
    user_id: Optional[str] = Field(default="test",description="用户id，立讯工号")
    stream: Optional[bool] = Field(default=False, description="是否使用流式响应")
    agent_config: Optional[AgentConfig] = None
    model: str = "default"
    file: Optional[list[str]] = None

# 对话响应模型
class ChatResponse(BaseModel):
    message: ChatMessage = Field(..., description="AI的响应消息")
    usage: Optional[dict] = Field(default=None, description="token使用统计")

# 流式接口响应数据模型
class ChatStreamResponse(BaseModel):
    content: str


# 服务端默认参数
DEFAULT_MAX_TOKENS = 8192

def build_system_prompt(agent_cfg: AgentConfig) -> str:
    """将 AgentConfig 转为一条简洁自然语言 system prompt"""
    name_part = f"你叫 {agent_cfg.agent_name}" if agent_cfg.agent_name else ""
    role_part = f"是一名{agent_cfg.agent_role}" if agent_cfg.agent_role else ""
    tone_part = f"回答请保持「{agent_cfg.agent_tone or '轻松'}」语气"
    desc_part = f"你有如下设定：{agent_cfg.agent_description}" if agent_cfg.agent_description else ""
    identity = "，".join(p for p in [name_part, role_part] if p) + "。"
    return f"{identity} {tone_part}。 {desc_part}"

def chat_stream(request: ChatRequest):
    """流式对话处理函数"""
    # 创建记录对象
    whole_process_recorder = WholeProcessRecorder()
    # 创建一个简化的QueryRequest对象以适配WholeProcessRecorder
    query_request = QueryRequest(
        user_id=request.user_id,  # 可以从request中获取或使用默认值
        question=request.messages[-1].content if request.messages else ""
    )
    whole_process_recorder.request = query_request
    whole_process_recorder.question_category = 0  # 通用对话类别
    whole_process_recorder.classification_reason = "聊天接口请求"

    # 注意：Token检查已移至FastAPI接口层
    if request.agent_config is not None:
        system_msg = ChatMessage(
            role="system",
            content=build_system_prompt(request.agent_config)
        )
        if request.messages and request.messages[0].role == "system":
            request.messages[0] = system_msg      # 覆盖原 system
        else:
            request.messages.insert(0, system_msg)  # 前插

    def chat_stream_response(content: str) -> str:
        response_data = ChatStreamResponse(content=content).model_dump_json()
        print(response_data)
        return f"data: {response_data}\n\n"

    processed_messages = process_messages_for_token_limit(request.messages)

    final_note = "\n\n#####最后提醒#####\n\n**请避免重复内容，不要连续输出空格，相同字符，或重复内容块**\n\n"
    processed_messages[-1].content = processed_messages[-1].content + final_note
    print("###输入prompt###：")
    print(processed_messages[-1].content)

    client = OpenAI(
        base_url=router.get_model_config("universal_chat",request.model).get("endpoint"),
        api_key=router.get_model_config("universal_chat",request.model).get("key")
    )
    thinking = router.get_model_config("universal_chat",request.model).get("thinking")
    
    models = client.models.list()
    model = models.data[0].id

    # 根据模型切换温度
    if "reasoning" in request.model:
        temperature = 0.7
    else:
        temperature = 0.0

    response = client.chat.completions.create(
        model=model,
        messages=[msg.dict() for msg in processed_messages],
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=temperature,
        stream=True,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": thinking},
        },
    )

    # 用于收集完整回复
    full_response = ""

    try:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                #print(repr(chunk.choices[0].delta.content))
                #yield f"data: {chunk.choices[0].delta.content}\n\n"
                #yield chat_stream_response(content=chunk.choices[0].delta.content)
                content = chunk.choices[0].delta.content
                full_response += content
                yield chat_stream_response(content=content)
    finally:
        # 发送结束标志
        #yield "data: [DONE]\n\n"
        # 完成记录
        from models.query import Answer, ContextSource
        whole_process_recorder.final_answer = Answer(
            is_question_answered=True,
            answer=full_response,
            contexts=[]  # 聊天接口没有上下文
        )
        whole_process_recorder.finish()

        # 保存到数据库
        error, res = insert_object(whole_process_recorder, "whole_process_records")
        if error:
            print(f"插入数据库错误：{error}\nWholeProcessRecorder:\n{whole_process_recorder}")
        yield chat_stream_response(content="[DONE]")


async def chat_non_stream(request: ChatRequest) -> ChatResponse:
    """非流式对话处理函数"""
    # 创建记录对象
    whole_process_recorder = WholeProcessRecorder()
    # 创建一个简化的QueryRequest对象以适配WholeProcessRecorder
    query_request = QueryRequest(
        user_id=request.user_id,  # 可以从request中获取或使用默认值
        question=request.messages[-1].content if request.messages else ""
    )
    whole_process_recorder.request = query_request
    whole_process_recorder.question_category = 0  # 通用对话类别
    whole_process_recorder.classification_reason = "聊天接口请求(非流式)"
    
    # 注意：Token检查已移至FastAPI接口层
    if request.agent_config is not None:
        system_msg = ChatMessage(
            role="system",
            content=build_system_prompt(request.agent_config)
        )
        if request.messages and request.messages[0].role == "system":
            request.messages[0] = system_msg      # 覆盖原 system
        else:
            request.messages.insert(0, system_msg)  # 前插
    
    # 先对消息列表进行处理，确保不会超出 token 限制
    processed_messages = process_messages_for_token_limit(request.messages)

    final_note = "\n\n#####最后提醒#####\n\n**请避免重复内容，不要连续输出空格，相同字符，或重复内容块**\n\n"
    processed_messages[-1].content = processed_messages[-1].content + final_note
    print("###输入prompt###：")
    print(processed_messages[-1].content)

    client = OpenAI(
        base_url=router.get_model_config("universal_chat",request.model).get("endpoint"),
        api_key=router.get_model_config("universal_chat",request.model).get("key")
    )
    
    thinking = router.get_model_config("universal_chat",request.model).get("thinking")
    
    models = client.models.list()
    model = models.data[0].id

    # 根据模型切换温度
    if "reasoning" in request.model:
        temperature = 0.7
    else:
        temperature = 0.0

    response = client.chat.completions.create(
        model=model,
        messages=[msg.dict() for msg in processed_messages],
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=temperature,
        stream=False,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": thinking},
        },
    )

    message_content = response.choices[0].message.content
    usage = response.usage.dict() if response.usage else None

    # 完成记录
    from models.query import Answer, ContextSource
    whole_process_recorder.final_answer = Answer(
        is_question_answered=True,
        answer=message_content,
        contexts=[]  # 聊天接口没有上下文
    )
    whole_process_recorder.finish()

    # 保存到数据库
    error, res = insert_object(whole_process_recorder, "whole_process_records")
    if error:
        print(f"插入数据库错误：{error}\nWholeProcessRecorder:\n{whole_process_recorder}")

    return ChatResponse(
        message=ChatMessage(role="assistant", content=message_content),
        usage=usage
    )


def generate_summary(text: str) -> str:
    """
    生成对话内容的摘要。

    Args:
        text: 需要摘要的文本

    Returns:
        str: 生成的摘要内容，或失败时的默认值
    """
    if not text.strip():
        return "无内容可摘要"

    summary_prompt = [
        {"role": "system", "content": "请将以下消息总结为一个简洁的摘要，保留关键信息，同时使用最少的字符数。"},
        {"role": "user", "content": text}
    ]
    try:

        client = OpenAI(
            base_url=router.get_model_config("universal_chat").get("endpoint"),
            api_key=router.get_model_config("universal_chat").get("key")
        )
        
        thinking = router.get_model_config("universal_chat").get("thinking")
        models = client.models.list()
        model = models.data[0].id

        summary_response = client.chat.completions.create(
            model=model,
            messages=summary_prompt,
            max_tokens=1000,
            temperature=0.7,
            stream=False,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": thinking},
            },
        )
        return summary_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"摘要生成失败: {e}")
        return "摘要生成失败"

def process_messages_for_token_limit(
    messages: List[ChatMessage],
    max_token_length: int = 23000,  # 改为token限制
    keep_recent: int = 3,
    max_summary_iters: int = 2
) -> List[ChatMessage]:
    """
    迭代式动态摘要，确保最终返回的消息列表总token数 ≤ max_token_length。
    - 每轮：对"旧消息"摘要，保留最近 keep_recent 条"新消息"原文；
    - 摘要后仍超限，将 processed_messages 作为新输入继续摘要，并将 keep_recent 递减，
      直到满足长度或 keep_recent=0（此时全量摘要）。
    - 若最终仍超限，则对最末摘要内容再做几轮"摘要的摘要"。

    Args:
        messages: 原始历史消息列表
        max_token_length: 最大token数限制
        keep_recent: 初始保留最近消息条数
        max_summary_iters: 最多对最终摘要再迭代压缩的次数

    Returns:
        List[ChatMessage]: 处理后可直接喂给 LLM 的消息列表
    """
    print("###进入摘要函数###")
    if not messages:
        print("无内容")
        return []

    from tokenizer_service import TokenCounter
    token_counter = TokenCounter()

    def total_length(msgs: List[ChatMessage]) -> int:
        if not msgs:
            return 0
        try:
            # 使用token计数服务计算token数
            return token_counter.count_chat([msg.dict() for msg in msgs])
        except Exception as e:
            print(f"Token计数失败，退回到字符计数方式: {str(e)}")
            # 如果token计数服务不可用，回退到字符计数
            return sum(len(m.content) for m in msgs)

    # 如果原始就没超限，直接返回
    if total_length(messages) <= max_token_length:
        print("历史记录没超限，直接返回")
        return messages

    # 初始化
    processed = messages[:]  # 用于迭代的消息列表
    k = min(keep_recent, len(processed))
    print("进行摘要...")
    # 逐轮摘要
    while total_length(processed) > max_token_length:
        # 当只剩下 1 条且仍超限时，直接摘要它本身
        if len(processed) == 1:
            text_to_summarize = processed[0].content
            summary = generate_summary(text_to_summarize)
            processed = [ChatMessage(role="system", content=f"对话摘要: {summary}")]
            break

        # 否则，将 processed 分为 "待摘要部分" + "保留部分"
        if len(processed) > k and k > 0:
            to_summarize = processed[:-k]
            to_keep     = processed[-k:]
        else:
            # k<=0 或 len(processed)<=k 时，全量摘要
            to_summarize = processed
            to_keep      = []

        # 拼接待摘要文本
        old_text = "\n".join(f"{m.role}: {m.content}" for m in to_summarize)
        summary = generate_summary(old_text)
        # 生成新的摘要消息
        processed = [ChatMessage(role="system", content=f"对话摘要: {summary}")] + to_keep

        # 递减 keep_recent，下一轮保留更少原文
        k = max(k - 1, 0)

    # 如果最终只有一条且仍超长，可再做几轮"摘要的摘要"
    if total_length(processed) > max_token_length and len(processed) == 1:
        for _ in range(max_summary_iters):
            raw = processed[0].content.replace("对话摘要: ", "")
            summary = generate_summary(raw)
            processed = [ChatMessage(role="system", content=f"对话摘要: {summary}")]
            if total_length(processed) <= max_token_length:
                break

    return processed
