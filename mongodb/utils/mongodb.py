from typing import Any

from bson.json_util import dumps
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from mongodb.utils.chunk_handler import CHUNK_SIZE, save_large_document, load_large_document

from configs.load import load_config

config = load_config()
mongodb_connection_string = config.get("mongodb").get("mongodb_connection_string")
username = "root"
password = "121314"
connection_str = f'mongodb://{username}:{password}@{mongodb_connection_string}/'


def get_client():
    try:
        client = MongoClient(connection_str, uuidRepresentation='standard')
        # 尝试获取服务器信息以验证连接
        client.admin.command('ismaster')
        return client
    except ConnectionFailure:
        print("MongoDB connection failed.")
        return None


def insert_data(db_name, collection_name, data, db_pool=None):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)

        serialized_data = dumps(data)
        if len(serialized_data.encode('utf-8')) > CHUNK_SIZE:
            # 如果整体超过 CHUNK_SIZE，进行分块存储
            save_large_document(data['_id'], data, getattr(db, f"{collection_name}_chunks"))
            # 存储主文档元数据
            result = collection.insert_one({"_id": data['_id'], "is_chunked": True})
        else:
            # 如果没有超过限制，直接存储
            result = collection.insert_one(data)

        doc_id = str(result.inserted_id)
        return True, doc_id
    except OperationFailure as e:
        return False, f"Error during insertion: {e}"
    finally:
        client.close()


def get_data_by_id(db_name, collection_name, uuid, db_pool=None):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        raw_data = collection.find_one({"_id": uuid})
        if not raw_data:
            return False, "No object found with given uuid."

        if raw_data.get("is_chunked"):
            # 如果是分块存储的文档，合并数据
            data = load_large_document(uuid, getattr(db, f"{collection_name}_chunks"))
        else:
            # 普通文档，直接使用
            data = raw_data
        return True, data
    finally:
        client.close()


def update_data_by_id(db_name, collection_name, uuid, update_data, db_pool=None):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        chunks_collection = getattr(db, f"{collection_name}_chunks")

        # 查询文档，判断是否分块存储
        existing_doc = collection.find_one({'_id': uuid})
        if not existing_doc:
            return False, "No object found with given uuid."

        # 合并现有文档和更新数据
        if existing_doc.get("is_chunked"):
            current_data = load_large_document(str(existing_doc['_id']), chunks_collection)
        else:
            current_data = existing_doc

        current_data.update(update_data)
        serialized_data = dumps(current_data)

        if len(serialized_data.encode('utf-8')) > CHUNK_SIZE:
            # 如果更新后文档大于 CHUNK_SIZE，重新分块存储
            chunks_collection.delete_many({'doc_id': str(existing_doc['_id'])})
            save_large_document(str(existing_doc['_id']), current_data, chunks_collection)
            collection.update_one(
                {'_id': uuid},
                {'$set': {"is_chunked": True}}
            )
        else:
            # 直接更新文档
            collection.update_one({'_id': uuid}, {'$set': current_data})

        return True, "Object updated successfully."
    finally:
        client.close()


def delete_data_by_id(db_name, collection_name, uuid):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        chunks_collection = getattr(db, f"{collection_name}_chunks")

        # 查询文档，判断是否分块存储
        existing_doc = collection.find_one({'_id': uuid})
        if not existing_doc:
            return False, "No object found with given uuid."

        if existing_doc.get("is_chunked"):
            # 删除所有相关分块
            chunks_collection.delete_many({'doc_id': str(existing_doc['_id'])})

        # 删除主文档
        result = collection.delete_one({'_id': uuid})
        if result.deleted_count == 0:
            return False, "No object found with given uuid."

        return True, "Object deleted successfully."
    finally:
        client.close()


def find_one_object(db_name, collection_name, *args: Any, db_pool=None, **kwargs: Any):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        chunks_collection = getattr(db, f"{collection_name}_chunks")

        data = collection.find_one(*args, **kwargs)
        if not data:
            return False, "No object found with given query."

        if data.get("is_chunked"):
            # 如果是分块存储，拼接数据
            data = load_large_document(str(data['_id']), chunks_collection)

        return True, data
    finally:
        client.close()


def find_objects(db_name, collection_name, *args: Any, db_pool=None, limit=None, **kwargs: Any):
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        chunks_collection = getattr(db, f"{collection_name}_chunks")

        cursor = collection.find(*args, **kwargs)

        if limit is not None and limit != 0:
            cursor = cursor.limit(limit)

        results = []

        for doc in cursor:
            if doc.get("is_chunked"):
                # 如果是分块存储，拼接数据
                full_doc = load_large_document(str(doc['_id']), chunks_collection)
                results.append(full_doc)
            else:
                results.append(doc)

        return True, results
    finally:
        client.close()


def get_all_objects(db_name: str, collection_name: str, db_pool=None) -> tuple:
    """
    获取指定数据库和集合中的所有文档。

    :param db_name: 数据库名称
    :param collection_name: 集合名称
    :param db_pool: 数据库连接池（可选）
    :return: (成功标志, 数据或错误消息)
    """
    client = get_client()
    if client is None:
        return False, "Connection to MongoDB failed."

    try:
        db = getattr(client, db_name)
        collection = getattr(db, collection_name)
        chunks_collection = getattr(db, f"{collection_name}_chunks")

        cursor = collection.find()  # 无条件查询所有文档
        results = []

        for doc in cursor:
            if doc.get("is_chunked"):
                # 如果是分块存储，拼接数据
                full_doc = load_large_document(str(doc['_id']), chunks_collection)
                results.append(full_doc)
            else:
                results.append(doc)

        return True, results
    finally:
        client.close()
