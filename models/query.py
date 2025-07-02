from typing import List, Optional, Dict, Annotated
import uuid
from pydantic import BaseModel, Field, create_model
from datetime import datetime


# Define request and response models
class QueryRequest(BaseModel):
    user_id: str
    question: str
    model: str = "default"

class QuestionClassification(BaseModel):
    category: int
    reason: str


class OptimizedQuestion(BaseModel):
    optimized_question: str
    info_to_collect: List[str]


class ContextSource(BaseModel):
    document_id: str
    document_title: str
    page: Optional[int] = None
    text: Optional[str] = None
    score: Optional[float] = -1.0

    def __str__(self):
        page_info = f", Page: {self.page}" if self.page is not None else ""
        score_info = f", Score: {self.score:.2f}" if self.score is not None else ""
        text_preview = f", Text: {self.text[:50]}..." if self.text else ""
        return f"ContextSource(Document: {self.document_title} {page_info}{score_info}{text_preview})"


class LLMAnswer(BaseModel):
    is_question_answered: bool = Field(..., description="问题是否可以很好地被回答")
    answer: Optional[str] = Field(None, description="如果信息足够，则提供答案")
    context_ids: List[int] = Field(..., description="参考的context编号列表")

    @property
    def has_answer(self) -> bool:
        return self.is_question_answered and self.answer is not None


class Answer(BaseModel):
    is_question_answered: bool = Field(..., description="问题是否可以很好地被回答")
    answer: Optional[str] = Field(None, description="如果信息足够，则提供答案")
    contexts: List[ContextSource] = Field(..., description="参考的context编号列表")


class StreamResponse(BaseModel):
    type: str
    content: str
    sources: Optional[List[ContextSource]] = Field(default=None)


class ReasoningJsonSchemaWrapper(BaseModel):
    reasoning: str
    answer: type[BaseModel]

    def create_wrapped_model(self):
        """
        根据 `answer` 生成一个新的 Pydantic 类，包含 `reasoning` 和 `answer` 的字段。
        """
        return create_model(
            f"Wrapped{self.answer.__name__}",  # 生成的类名
            reasoning=(Annotated[str, Field(description="思考或推理过程")], ...),  # 强制必须有 `reasoning` 字段
            answer=(Annotated[self.answer, Field(description="正式回答")], ...)  # `answer` 作为 `BaseModel` 类型的字段
        )

class RecordQueryParams(BaseModel):
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")

class WholeProcessRecorder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="id")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    request: Optional[QueryRequest] = Field(default=None)

    question_category_reasoning: Optional[str] = Field(default="")
    question_category: Optional[int] = Field(default=-1)
    classification_reason: Optional[str] = Field(default="")

    question_optimization_reasoning: Optional[str] = Field(default="")
    optimized_question: Optional[str] = Field(default="")
    info_to_collect: Optional[List[str]] = Field(default=None)

    retrieved_contexts_all: Optional[List[List[Dict]]] = Field(default_factory=list)
    retrieved_contexts: Optional[List[ContextSource]] = Field(default_factory=list)

    final_answer: Optional[Answer] = Field(default=None)

    end_time: Optional[datetime] = Field(default=None)

    def finish(self):
        self.end_time = datetime.utcnow()

    def __str__(self):
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else None
        return (
            f"🔹 **全过程记录**\n"
            f"🆔 记录ID: {self.id}\n"
            f"🆔 用户ID: {self.request.user_id}\n"
            f"⏳ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"✍️ 原始问题: {self.request.question}\n"
            f"✍️ 优化后问题: {self.optimized_question}\n"
            f"📌 问题分类: {self.question_category}（理由: {self.classification_reason}）\n"
            f"🔍 需要收集的信息: {'; '.join(self.info_to_collect) if self.info_to_collect else '无'}\n"
            f"📚 召回上下文 (全部): {len(self.retrieved_contexts_all)} 组\n"
            f"📖 召回上下文 (筛选后): {len(self.retrieved_contexts)} 条\n"
            f"✅ 是否回答: {self.final_answer.is_question_answered}\n"
            f"✅ 最终答案: {self.final_answer.answer}\n"
            f"⏳ 结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else '进行中'}\n"
            f"⏱ 耗时: {f'{duration:.2f} 秒' if duration is not None else '进行中'}"
        )

