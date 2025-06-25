import re
from typing import List

from models.document import Page, Chunk, DocumentType


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
def generate_chunks_for_page(page: Page) -> List[Chunk]:
    if not page.page_text:
        return []

    chunk_size = 50
    overlap = 10
    min_last_chunk = 25

    chunk_texts = generate_chunks_from_text(page.page_text, chunk_size, overlap, min_last_chunk)
    chunks = []
    for i, text in enumerate(chunk_texts):
        chunk_obj = Chunk(
            page_id=page.id,
            document_id=page.document_id,
            page_num=page.page_num,
            chunk_doc_type=DocumentType.HR_INFO,  # 固定为 HR-Info
            chunk_doc_publish_date=None,
            chunk_text=text,
            chunk_embedding=None,
            overlap_words_count=overlap if i > 0 else 0  # 除第一个 chunk 外重叠 token 数为 overlap
        )
        chunks.append(chunk_obj)
    return chunks


# 示例使用
if __name__ == "__main__":
    sample_text = '''
    在当今全球化时代，cultural exchange has become more prevalent than ever before. 人们越来越意识到不同文化之间的差异和共性。例如，在艺术和文学领域，Eastern traditions often blend seamlessly with Western innovation, resulting in a fascinating tapestry of creativity. The digital revolution accelerates these interactions as information flows freely across borders and languages.

Artificial intelligence, or AI, is one of the key drivers of change. 从智能手机到自动驾驶汽车，the impact of AI touches almost every aspect of our daily lives. Researchers worldwide are not only focused on technical improvements but are also deeply engaged with the ethical implications of these advancements. 同时，在学术界和工业界，interdisciplinary collaboration is encouraged, merging insights from computer science, philosophy, psychology, and more to foster holistic solutions and a better understanding of human behavior.

与此同时，environmental concerns have become central to global debates. Global warming, pollution, and the depletion of natural resources demand urgent action. Scientists across continents are dedicating themselves to developing sustainable technologies that can mitigate human impact on our planet. Renewable energy sources, such as solar and wind power, are emerging as viable alternatives to fossil fuels. 政府和非政府组织也在积极推动各种绿色项目，以期实现未来的可持续发展。

在教育领域，innovative teaching methods are transforming how students learn and grow. Online education platforms and digital resources democratize knowledge, making it accessible to people regardless of geography. 随着技术不断进步，传统课堂正在逐步转变为更加互动和个性化的学习环境。Educators are experimenting with blended learning models that combine the advantages of in-person instruction with the flexibility of online courses, thus enhancing critical thinking and creativity.

Social interactions, too, have evolved with the rise of social media. 虽然这种全新的交流方式有时会引发误解和冲突，但它也为人们提供了跨越地域和文化界限建立联系与合作的机会。Communities are forming around shared interests, enabling vibrant discussions and new ideas. In this digital age, it remains essential to balance online communication with genuine face-to-face interactions, nurturing empathy and mutual respect.

总体而言，我们的现代世界充满了变革与挑战，也孕育着前所未有的机遇。The fusion of Eastern wisdom and Western innovation, alongside insights from diverse disciplines, creates a dynamic environment for progress and creativity. Embracing diversity, sustainable development, and lifelong learning are the keys to navigating this era of uncertainty and transformation.
    '''
    page = Page(document_id="doc_123", page_num=1, page_text=sample_text)
    chunks = generate_chunks_for_page(page)

    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx + 1}: {chunk.chunk_text}")