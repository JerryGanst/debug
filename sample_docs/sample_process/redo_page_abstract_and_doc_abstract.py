from typing import List

from llm_tasks.page_abstract import generate_page_abstract
from models.document import Document
from mongodb.ops.object_op import get_objects_by_conditions, update_object
from sample_docs.sample_process.doc_abstract import get_pages_of_document, fill_document_abstract
from sample_docs.sample_process.utils import count_words

if __name__ == "__main__":
    conditions = {"file_type": "pdf"}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        print(error)
        exit()

    documents: List[Document]
    print(len(documents))

    # for doc in documents:
    #     if doc.id != "b4ad9a6e-c6a6-4126-86c8-879b88ee8cda":
    #         continue
    #     print(f"现在处理 page-abstract：《{doc.title}》...")
    #     pages = get_pages_of_document(doc)
    #     # doc.pages = len(pages)
    #     # update_object(doc.id, doc, "documents")
    #     for idx, page in enumerate(pages):
    #         print(f"    - 第 {idx + 1} 页")
    #         text_length, text_words = count_words(page.page_text)
    #         if text_length <= 400:
    #             print(f"原文字数少，不生成摘要!")
    #             page.abstract = page.page_text
    #         else:
    #             page.abstract = generate_page_abstract(page.page_text)
    #         update_object(page.id, page, "pages")

    for doc in documents:
        if doc.id != "b4ad9a6e-c6a6-4126-86c8-879b88ee8cda":
            continue
        print(f"现在处理 doc-abstract：《{doc.title}》...")
        fill_document_abstract(doc)