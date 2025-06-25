import requests

from models.document import Document, Chunk, Page
from mongodb.ops.object_op import get_objects_by_conditions, delete_object
from configs.load import load_config
config = load_config()
BASE_URL = config.get("context_retrieval").get("weaviate_endpoint")
# BASE_URL = "http://10.1.4.248:8080"


def rm_one_document_from_weaviate_by_id(document_id: str):
    try:
        params = {
            'uuid': document_id,
        }
        resp = requests.post(f"{BASE_URL}/v1/document/delete", json=params)
        if resp.status_code == 200:
            print(f"weaviate条目成功删除：{document_id}")
    except Exception as e:
        print(f"weaviate条目删除失败：{document_id}")


def rm_one_document_from_weaviate_by_title(document_title: str):
    try:
        params = {
            'doc_title': document_title,
        }
        resp = requests.post(f"{BASE_URL}/v1/document/delete", json=params)
        if resp.status_code == 200:
            print(f"weaviate条目成功删除：{document_title}")
    except Exception as e:
        print(f"weaviate条目删除失败：{document_title}")


def rm_one_document_from_mongodb_by_id(document_id: str):

    error, result = delete_object(document_id, "documents")
    if error:
        print(f"ERROR: 删除document失败：{document_id}")

    conditions = {"document_id": document_id}
    error, pages = get_objects_by_conditions(conditions, Page, "pages")
    if error:
        print(f"ERROR: 取回document的Page失败：{document_id}")
        return
    print(f"成功删除文档： {document_id}")

    for page in pages:
        error, result = delete_object(page.id, 'pages')
        if error:
            print(f"ERROR: 删除page失败：{document_id} - {page.id}")
    print(f"成功删除文档相关 pages： {document_id}")

    error, chunks = get_objects_by_conditions(conditions, Chunk, "chunks")
    for chunk in chunks:
        error, result = delete_object(chunk.id, 'chunks')
        if error:
            print(f"ERROR: 删除chunk失败：{document_id} - {chunk.id}")
    print(f"成功删除文档相关 chunks： {document_id}")


def rm_one_document_from_mongodb_by_title(document_title: str):
    conditions = {"title": document_title}
    error, existing_docs = get_objects_by_conditions(conditions, Document, "documents")
    print(f"找到 {len(existing_docs)} 条该title记录： {document_title}")
    if not error and existing_docs:
        for doc in existing_docs:
            rm_one_document_from_mongodb_by_id(doc.id)
        print(f"成功删除该title的文档相关： {document_title}")


def rm_one_document_from_both_by_title(document_title: str):
    rm_one_document_from_mongodb_by_title(document_title)
    rm_one_document_from_weaviate_by_title(document_title)



if __name__ == "__main__":
    conditions = {"doc_type": "IT"}
    error, docs = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        print("查询doc_type为IT的文档失败")
    else:
        print(f"找到 {len(docs)} 条doc_type为IT的文档")
        for doc in docs:
            rm_one_document_from_mongodb_by_id(doc.id)
