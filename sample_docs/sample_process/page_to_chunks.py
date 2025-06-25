from models.document import Document
from mongodb.ops.object_op import get_object_by_id, insert_object, update_object, get_objects_by_conditions
from sample_docs.sample_process.chunk_utils import generate_chunks_for_page
from sample_docs.sample_process.doc_abstract import get_pages_of_document


def chunk_for_document(document: Document, enforce_rechunk=False):
    pages = get_pages_of_document(document)
    for idx, page in enumerate(pages):
        if page.chunked:
            print(f"第 {idx+1} 页已经 chunk")
            continue

        print(f"正在 chunk 第 {idx+1} 页 text")
        chunks = generate_chunks_for_page(page, document)
        for chunk in chunks:
            # chunk.chunk_embedding = embedding_chunk(chunk.chunk_text)
            insert_object(chunk, "chunks")
        page.chunked = True
        update_object(page.id, page, "pages")


if __name__ == "__main__":
    # error, doc = get_object_by_id("99013ac6-f6a4-4a5d-b5c7-32c756927522", Document, "documents")
    # print(doc)
    # doc: Document
    # chunk_for_document(doc)

    conditions = {"processed_to_pages": True, "file_type": "pdf", "id": "b4ad9a6e-c6a6-4126-86c8-879b88ee8cda"}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    print(len(documents))
    for doc in documents:
        print(doc.title)
        pages = get_pages_of_document(doc)
        # for page in pages:
        #     page.chunked = False
        #     update_object(page.id, page, "pages")
        chunk_for_document(doc)
