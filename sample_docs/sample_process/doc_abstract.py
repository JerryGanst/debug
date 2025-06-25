from typing import List

from llm_tasks.document_abstract import generate_document_abstract
from models.document import Document, Page
from mongodb.ops.object_op import get_objects_by_conditions, update_object


def get_pdfs_without_abstract() -> List[Document]:
    conditions = {"processed_to_pages": True, "file_type": "pdf", "abstract": None}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        return []
    documents: List[Document]
    return documents


def get_pages_of_document(document: Document) -> List[Page]:
    conditions = {"document_id": document.id}
    error, pages = get_objects_by_conditions(conditions, Page, "pages")
    if error:
        return []
    pages: List[Page]
    pages.sort(key=lambda page: page.page_num)
    return pages


def fill_document_abstract(document: Document):
    pages = get_pages_of_document(document)
    page_abstracts = "\n".join([f"第{page.page_num}页：{page.abstract}" for page in pages])

    # 计算文本长度，假设中文字符与token 1:1对应
    max_token_limit = 13000 - 900  # 考虑提示词占用约900 tokens

    # 如果文本长度超过限制，进行分段处理
    if len(page_abstracts) > max_token_limit:
        # 分段处理文本
        segments = []
        current_segment = ""

        # 按页分割，确保每段不超过token限制
        for page in pages:
            page_text = f"第{page.page_num}页：{page.abstract}"

            # 如果添加当前页会超出限制，先处理当前段
            if len(current_segment) + len(page_text) > max_token_limit and current_segment:
                segments.append(current_segment)
                current_segment = page_text
            else:
                current_segment += "\n" + page_text if current_segment else page_text

        # 添加最后一段
        if current_segment:
            segments.append(current_segment)

        # 为每段生成摘要
        segment_abstracts = []
        for i, segment in enumerate(segments):
            print(f"处理第{i + 1}/{len(segments)}段文本...")
            segment_abstract = generate_document_abstract(
                f"{document.title} (第{i + 1}部分，共{len(segments)}部分)",
                segment
            )
            segment_abstracts.append(segment_abstract)

        # 合并所有段落摘要，再生成最终摘要
        combined_abstracts = "\n\n".join([
            f"第{i + 1}部分摘要：{abstract}"
            for i, abstract in enumerate(segment_abstracts)
        ])

        # 生成最终文档摘要
        document_abstract = generate_document_abstract(
            f"{document.title} (汇总摘要)",
            combined_abstracts
        )
    else:
        # 如果文本长度在限制范围内，直接生成摘要
        document_abstract = generate_document_abstract(document.title, page_abstracts)

    document.abstract = document_abstract
    print(document_abstract)
    update_object(document.id, document, "documents")


if __name__ == "__main__":
    docs = get_pdfs_without_abstract()
    fill_document_abstract(docs[0])