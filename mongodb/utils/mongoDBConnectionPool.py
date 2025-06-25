import traceback
from typing import Union, Tuple, Any
from pymongo import MongoClient
from dbutils.pooled_db import PooledDB
from pymongo.errors import ConnectionFailure, PyMongoError


class MongoDBConnectionPool:
    def __init__(self, host='localhost', port=27017, username=None, password=None, max_connections=5, **kwargs):
        """
        初始化MongoDB连接池
        :param host: MongoDB服务器地址
        :param port: MongoDB服务器端口
        :param username: MongoDB数据库用户名
        :param password: MongoDB数据库密码
        :param max_connections: 连接池允许的最大连接数
        :param kwargs: 传递给MongoClient的其他参数
        """
        try:
            self.pool = PooledDB(
                creator=MongoClient,
                maxconnections=max_connections,
                host=host,
                port=port,
                username=username,
                password=password,
                authSource='admin',  # 默认情况下，MongoDB的身份验证数据库是'admin'
                **kwargs
            )
        except PyMongoError as e:
            print(f"创建连接池失败: {str(e)} - {traceback.format_exc()}")
            raise

    def get_connection(self) -> Tuple[Union[None, str], Any]:
        """
        从连接池中获取一个MongoDB连接
        :return: MongoClient实例
        """
        try:
            return None, self.pool.connection()
        except PyMongoError as e:
            error_info = f"DB_Pool: 从pool获取连接失败\nException: {str(e)}\nTraceback: {traceback.format_exc()}"
            return error_info, None

    def close(self):
        """
        关闭连接池
        """
        try:
            self.pool.close()
        except Exception as e:
            print(f"Failed to close connection pool: {e}")

    def insert_document(self, db_name, collection_name, document):
        """
        插入一个文档到指定的数据库和集合中
        """
        try:
            with self.get_connection() as client:
                db = client[db_name]
                collection = db[collection_name]
                result = collection.insert_one(document)
                return result.inserted_id
        except PyMongoError as e:
            print(f"Failed to insert document: {e}")
            raise

    def update_document(self, db_name, collection_name, query, update_values):
        """
        更新指定数据库和集合中的文档
        """
        try:
            with self.get_connection() as client:
                db = client[db_name]
                collection = db[collection_name]
                result = collection.update_one(query, {'$set': update_values})
                return result.modified_count
        except PyMongoError as e:
            print(f"Failed to update document: {e}")
            raise

    def retrieve_documents(self, db_name, collection_name, query):
        """
        从指定数据库和集合中检索文档
        """
        try:
            with self.get_connection() as client:
                db = client[db_name]
                collection = db[collection_name]
                documents = list(collection.find(query))
                return documents
        except PyMongoError as e:
            print(f"Failed to retrieve documents: {e}")
            raise


# 使用示例
if __name__ == "__main__":
    pass
