from bson import ObjectId
from bson.json_util import dumps, loads
CHUNK_SIZE = 15 * 1024 * 1024  # 16MB


def save_large_document(doc_id: str, data: dict, chunk_collection):
    """将大文档拆分为多个子文档存储"""
    import json

    serialized_data = dumps(data)
    for i in range(0, len(serialized_data), CHUNK_SIZE):
        chunk = {
            "doc_id": doc_id,
            "chunk_index": i // CHUNK_SIZE,
            "data": serialized_data[i:i + CHUNK_SIZE]
        }
        chunk_collection.insert_one(chunk)


def load_large_document(doc_id: str, chunk_collection) -> str:
    """从多个子文档中合并出完整文档"""
    chunks = chunk_collection.find({"doc_id": doc_id}).sort("chunk_index")
    serialized_data = ''.join(chunk['data'] for chunk in chunks)
    return loads(serialized_data)