from typing import List

from models.document import Document, Page, Chunk
import requests

from mongodb.ops.object_op import update_object, get_objects_by_conditions
from configs.load import load_config

config = load_config()
url = config.get("context_retrieval").get("embedding_endpoint")
# url = "http://10.180.116.172:8000/embed/"


def doc_embed(document: Document):
    params = {"text": document.abstract}
    response = requests.post(url, params=params)
    embedding_result = response.json().get('embedding')
    document.abstract_embedding = embedding_result
    update_object(document.id, document, "documents")


def page_embed(page: Page):
    params = {"text": page.abstract}
    response = requests.post(url, params=params)
    embedding_result = response.json().get('embedding')
    page.abstract_embedding = embedding_result
    update_object(page.id, page, "pages")


def chunk_embed(chunk: Chunk):
    params = {"text": chunk.chunk_text}
    response = requests.post(url, params=params)
    embedding_result = response.json().get('embedding')
    chunk.chunk_embedding = embedding_result
    update_object(chunk.id, chunk, "chunks")


if __name__ == "__main__":
    # conditions = {"file_type": "pdf"}
    # error, documents = get_objects_by_conditions(conditions, Document, "documents")
    # if error:
    #     print(error)
    #     exit()
    # print(len(documents))
    # for doc in documents:
    #     doc_embed(doc)

    # error, pages = get_objects_by_conditions({}, Page, "pages")
    # if error:
    #     print(error)
    #     exit()
    # for page in pages:
    #     page_embed(page)

    error, chunks = get_objects_by_conditions({"document_id": "b4ad9a6e-c6a6-4126-86c8-879b88ee8cda"}, Chunk, "chunks")
    if error:
        print(error)
        exit()

    print(len(chunks))
    for chunk in chunks:
        chunk_embed(chunk)


