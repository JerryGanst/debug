import re
from typing import List

from models.document import Page, Chunk, Document


# 分词函数：匹配中文单个字符或连续的英文单词／数字
def tokenize(text: str) -> List[str]:
    # 匹配中文汉字和英文单词（字母或数字）
    pattern = re.compile(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+')
    tokens = pattern.findall(text)
    return tokens


# 重构文本函数：根据 token 类型决定是否在英文 token 间添加空格
def reconstruct_text(tokens: List[str]) -> str:
    # 判断 token 是否为英文单词/数字
    def is_english(token: str) -> bool:
        return re.fullmatch(r'[a-zA-Z0-9]+', token) is not None

    if not tokens:
        return ""
    result = tokens[0]
    prev = tokens[0]
    for token in tokens[1:]:
        if is_english(prev) and is_english(token):
            result += " " + token
        else:
            result += token
        prev = token
    return result


# 根据规则生成 chunk 文本列表
def generate_chunks_from_text(text: str, chunk_size: int = 50, overlap: int = 10, min_last_chunk: int = 25) -> List[
    str]:
    tokens = tokenize(text)
    chunks = []
    start = 0
    n = len(tokens)

    while start < n:
        end = start + chunk_size
        if end >= n:
            # 如果剩余 token 数不足一个完整 chunk
            if n - start < min_last_chunk and chunks:
                # 将不足的部分并入前一个 chunk
                chunks[-1].extend(tokens[start:])
            else:
                chunks.append(tokens[start:n])
            break
        else:
            chunks.append(tokens[start:end])
            start = end - overlap  # 重叠部分
    # 利用 reconstruct_text 还原文本，确保英文之间空格正常
    return [reconstruct_text(chunk) for chunk in chunks]


# 根据 Page 对象生成 Chunk 对象列表
def generate_chunks_for_page(page: Page, doc: Document) -> List[Chunk]:
    if not page.page_text:
        return []

    chunk_size = 250
    overlap = 50
    min_last_chunk = 150

    chunk_texts = generate_chunks_from_text(page.page_text, chunk_size, overlap, min_last_chunk)
    chunks = []
    for i, text in enumerate(chunk_texts):
        chunk_obj = Chunk(
            page_id=page.id,
            document_id=page.document_id,
            page_num=page.page_num,
            chunk_doc_type=doc.doc_type,  # 根据doc的doc_type自适应
            chunk_doc_publish_date=doc.publish_date,
            chunk_text=text,
            chunk_embedding=None,
            chunk_size=chunk_size,
            overlap_words_count=overlap if i > 0 else 0  # 除第一个 chunk 外重叠 token 数为 overlap
        )
        chunks.append(chunk_obj)
    return chunks
