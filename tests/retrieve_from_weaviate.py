import requests

from models.query import ContextSource

WEAVIATE_URL = "http://127.0.0.1:8085"
EMBEDDING_URL = "http://10.180.116.172:8000/embed/"

# 插入文档

if __name__ == "__main__":

    # query = "员工工作时间是多少？"
    query = "LDP"

    params = {"text": query}
    response = requests.post(EMBEDDING_URL, params=params)
    query_embedding = response.json().get('embedding')
    print(query_embedding)

    filters = {
        "chunk_doc_type": "IT",
        'contents': [query_embedding],
        'topK': 5
    }
    resp = requests.post(f"{WEAVIATE_URL}/v1/chunk/get_chunks", json=filters)

    res = resp.json()
    print(res)
    print(resp.status_code)  # 打印响应信息
    print(len(res))

    retrieved_contexts = []

    for rr in res:
        cur_query_contexts = []
        for r in rr:
            cur_query_contexts.append(ContextSource(
                document_id=r['document']['id'],
                document_title=r['document']['title'],
                page=r['page_num'],
                text=r['chunk_text'],
                score=r['distance']
            ))
        retrieved_contexts.append(cur_query_contexts)

    retrieved_contexts = [item for sublist in retrieved_contexts for item in sublist]
    for rc in retrieved_contexts:
        print(rc)