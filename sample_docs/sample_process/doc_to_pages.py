from typing import List

from llm_tasks.page_abstract import generate_page_abstract
from llm_tasks.refine_page_text import refine_text_with_llm
from models.document import Document, Page
from mongodb.ops.object_op import get_objects_by_conditions, insert_object, update_object
from sample_docs.sample_process.doc_abstract import fill_document_abstract, get_pages_of_document
from sample_docs.sample_process.utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_pptx,
    remove_vietnamese_text,
    count_words
)


# 处理文档，将其拆分为 Page 对象
def document_to_pages(document: Document, overlap_words_count: int = 50) -> List[Page]:
    """将文档分页，并加上前一页的最后 50 个字"""
    pages = get_pages_of_document(document)

    # Determine the file type and extract text accordingly
    if document.file_path.endswith('.pdf'):
        text_pages = extract_text_from_pdf(document.file_path)
    elif document.file_path.endswith(('.doc', '.docx')):
        text_pages = extract_text_from_docx(document.file_path)
    elif document.file_path.endswith(('.ppt', '.pptx')):
        text_pages = extract_text_from_pptx(document.file_path)
    else:
        raise ValueError("Unsupported file type")

    previous_tail = ("", 0) # 上一页的overlap文字和字数
    for i, text in enumerate(text_pages):
        if i < len(pages):
            print(f"第 {i+1} 页已经处理过...")
            continue
        # print(f"PreviousTail: {previous_tail}")

        print(f"processing page {i+1}...", flush=True)
        text = remove_vietnamese_text(text)  # 处理越南语
        text = refine_text_with_llm(text)
        print(f"text length: {len(text)}")
        word_count, text_words = count_words(text)  # 计算 word_count

        # 计算 overlap
        if previous_tail[0]:
            full_text = previous_tail[0] + text
            total_word_count = word_count + previous_tail[1]
        else:
            full_text = text
            total_word_count = word_count

        if total_word_count <= 400:
            print(f"原文字数少，不生成摘要!")
            page_abstract = full_text
        else:
            page_abstract = generate_page_abstract(full_text)

        # 生成 Page 对象
        page = Page(
            document_id=document.id,
            page_num=i + 1,
            page_text=full_text.strip(),
            word_count=total_word_count,
            overlap_words_count=previous_tail[1] if previous_tail[0] else 0,
            abstract=page_abstract
        )

        insert_object(page, "pages")
        pages.append(page)

        # 更新 previous_tail（按字符数截取）
        if word_count > overlap_words_count:
            previous_tail = ("".join(text_words[-overlap_words_count:]), overlap_words_count)
        else:
            previous_tail = (text, word_count)

    document.pages = len(pages)
    document.processed_to_pages = True
    update_object(document.id, document, "documents")
    return pages


if __name__ == "__main__":
    conditions = {"file_type": "pptx"}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        print(error)
        exit()

    documents: List[Document]
    for document in documents:
        pages = get_pages_of_document(document)
        document.pages = len(pages)
        update_object(document.id, document, "documents")