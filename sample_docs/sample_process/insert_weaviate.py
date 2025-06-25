import requests

from models.document import Document, Chunk, Page
from mongodb.ops.object_op import get_objects_by_conditions
from configs.load import load_config
config = load_config()
BASE_URL = config.get("context_retrieval").get("weaviate_endpoint")
# BASE_URL = "http://localhost:8080"

if __name__ == "__main__":
    conditions = {}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        print(error)
        exit()

    for doc in documents:
        #       print(doc)
        resp = requests.post(f"{BASE_URL}/v1/document/insert", json=doc.model_dump())
        print(resp.status_code, resp.json())  # 打印响应信息
    #        exit()

    error, pages = get_objects_by_conditions({}, Page, "pages")
    if error:
        print(error)
        exit()

    for page in pages:
        resp = requests.post(f"{BASE_URL}/v1/page/insert", json=page.model_dump())
        print(resp.status_code, resp.json())  # 打印响应信息
        # break

    error, chunks = get_objects_by_conditions({}, Chunk, "chunks")
    if error:
        print(error)
        exit()

    for chunk in chunks:
        resp = requests.post(f"{BASE_URL}/v1/chunk/insert", json=chunk.model_dump())
        print(resp.status_code, resp.json())  # 打印响应信息
        # break
