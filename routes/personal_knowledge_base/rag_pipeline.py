import os, asyncio, tempfile, pathlib, time
from typing import List
from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from minio import Minio
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain

from configs.load import load_config, ModelRouter
from models.query import ContextSource, StreamResponse
from routes.personal_knowledge_base.embeddings import RemoteBGEEmbeddings
from tokenizer_service import TokenCounter

# -----------------------------------------------------------------------------
# 配置加载
# -----------------------------------------------------------------------------
config = load_config()
model_router = ModelRouter(config)

# ---------- MinIO ----------
MINIO_ENDPOINT = config.get("minio").get("minio_endpoint")
MINIO_ACCESS_KEY = config.get("minio").get("minio_access_key")
MINIO_SECRET_KEY = config.get("minio").get("minio_secret_key")
MINIO_BUCKET = config.get("minio").get("minio_bucket")

minio_client = Minio(
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    secure=False,
)

# ---------- 常量 ----------
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
ALLOWED_SUFFIXES = {".txt", ".pdf"}

# ---------- FastAPI ----------
router = APIRouter(tags=["personal_rag"])

# ---------- Token 计数器 ----------

token_counter = TokenCounter()

# -----------------------------------------------------------------------------
# 数据模型
# -----------------------------------------------------------------------------


class RAGRequest(BaseModel):
    user_id: str
    question: str
    model: str
    objects: List[str]


class RAGResponse(BaseModel):
    answer: str
    sources: List[str]


# -----------------------------------------------------------------------------
# 工具函数
# -----------------------------------------------------------------------------

def _object_to_documents(obj: str) -> List[Document]:
    """从 MinIO 下载对象并转换为 Document 列表。"""
    raw = minio_client.get_object(MINIO_BUCKET, obj).read()
    suffix = pathlib.Path(obj).suffix.lower()

    if suffix == ".txt":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(raw)
            path = f.name
        docs = TextLoader(path, autodetect_encoding=True).load()
    elif suffix == ".pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(raw)
            path = f.name
        docs = PyPDFLoader(path).load()
    else:  # 理论上不会走到这里，防御性兜底
        docs = splitter.create_documents([raw.decode("utf-8", errors="ignore")])

    for d in docs:
        d.metadata["source"] = obj
    return docs


def create_stream_response(
    type: str,
    content: str,
    sources: List[ContextSource] | None = None,
) -> str:
    response_data = StreamResponse(type=type, content=content, sources=sources).model_dump_json()
    return f"data: {response_data}\n\n"


# -----------------------------------------------------------------------------
# 核心 RAG 逻辑（带计时）
# -----------------------------------------------------------------------------


async def rag(req: RAGRequest):
    """RAG 主流程（流式返回），并在关键步骤输出耗时。"""

    overall_start = time.perf_counter()

    # 0️⃣ 参数校验
    if not req.objects:
        raise HTTPException(400, "objects 不能为空")

    filtered = [o for o in req.objects if pathlib.Path(o).suffix.lower() in ALLOWED_SUFFIXES]
    if not filtered:
        raise HTTPException(400, "仅支持 txt / pdf 文件")

    # 1️⃣ 下载并转 Document ------------------------------------------------------
    yield create_stream_response(type="process", content="开始加载个人知识库文档...")
    t0 = time.perf_counter()

    docs: List[Document] = []
    for obj in filtered:
        try:
            docs.extend(_object_to_documents(obj))
        except Exception as e:
            raise HTTPException(404, f"{obj} 下载失败: {e}")

    t1 = time.perf_counter()
    yield create_stream_response(type="process", content=f"文档加载完成，用时 {t1 - t0:.2f}s")

    # 2️⃣ 构建向量库 -----------------------------------------------------------
    yield create_stream_response(type="process", content="正在构建向量数据库...")
    t2_start = time.perf_counter()

    embedder = RemoteBGEEmbeddings()
    vectordb = Chroma.from_documents(docs, embedder)

    t2_end = time.perf_counter()
    yield create_stream_response(type="process", content=f"向量数据库构建完成，用时 {t2_end - t2_start:.2f}s")

    # 3️⃣ 初始化 LLM 与 RAG Chain ---------------------------------------------
    t3_start = time.perf_counter()

    cfg = model_router.get_model_config("personal_knowledge_base", req.model)

    llm = ChatOpenAI(
        base_url=cfg["endpoint"],
        api_key=cfg["key"],
        model=cfg["model_name"],
        temperature=cfg["temperature"],
        extra_body={
            "presence_penalty": 0.3,  # 鼓励新信息
            "repetition_penalty": 1.1,  # vLLM 支持，减少复读
            "chat_template_kwargs": {"enable_thinking": cfg["thinking"]},
        },
    )

    RICH_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "### 角色\n"
            "你是一名 **资深知识库顾问**，擅长把分散资料整理成条理清晰的洞见。\n\n"
            "### 任务\n"
            "1. **深度思考**（勿输出思考痕迹）。\n"
            "2. 按下列六节输出 _Markdown_：\n"
            "   - ## 一句话概览  \n"
            "   - ## 背景  \n"
            "   - ## 关键要点（要点用列表）  \n"
            "   - ## 示例 / 类比（≥1 个，便于理解）  \n"
            "   - ## 注意事项（风险、限制）  \n"
            "   - ## 结论（重申核心 + 下一步建议）  \n"
            "3. 若资料不足，请在『注意事项』声明“不确定”并提出后续调查方向。\n\n"
            "### 资料\n"
            "{context}\n\n"
            "### 用户问题\n"
            "{question}\n\n"
            "### 回答（中文）："
        ),
    )

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": RICH_PROMPT, "document_variable_name": "context"},
    )

    t3_end = time.perf_counter()
    yield create_stream_response(type="process", content=f"RAG chain 构建完成，用时 {t3_end - t3_start:.2f}s")
    yield create_stream_response(type="process", content="开始检索并生成答案...")

    # 4️⃣ 执行链 ---------------------------------------------------------------
    t4_start = time.perf_counter()
    result = await asyncio.to_thread(chain, {"question": req.question})
    t4_end = time.perf_counter()

    answer = result["answer"]
    sources = sorted({d.metadata["source"] for d in result["source_documents"]})
    sources_cs = [ContextSource(document_id="-1", document_title=item) for item in sources]

    yield create_stream_response(type="process", content=f"答案生成完成，用时 {t4_end - t4_start:.2f}s")
    yield create_stream_response(type="final_answer", content=answer, sources=sources_cs)

    # 5️⃣ 总耗时 ---------------------------------------------------------------
    total = time.perf_counter() - overall_start
    yield create_stream_response(type="process", content=f"本次查询总耗时 {total:.2f}s")


# -----------------------------------------------------------------------------
# FastAPI 路由封装
# -----------------------------------------------------------------------------


@router.post("/personal_rag")
async def process_personal_rag(req: RAGRequest):
    # 检查输入 question 的 token 数
    token_count = token_counter.count_text(req.question)
    if token_count > token_counter.token_limit:
        return JSONResponse(
            status_code=400,
            content={
                "error": "输入 token 超过限制",
                "token_count": token_count,
                "token_limit": token_counter.token_limit,
            },
        )

    return StreamingResponse(rag(req), media_type="text/event-stream")