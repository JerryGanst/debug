from typing import Union, List, Tuple, Type

from pydantic import BaseModel

from mongodb.utils.mongodb import insert_data, get_data_by_id, find_objects, update_data_by_id, delete_data_by_id


# 辅助方法：将 MongoDB 的返回结果转换为对象
def _get_object_from_res(res, obj_class: Type[BaseModel]) -> Tuple[Union[None, str], Union[BaseModel, None]]:
    try:
        # 直接用 Pydantic 的 parse_obj 来创建对象
        return None, obj_class.parse_obj(res)
    except Exception as e:
        return str(e), None


# 增：插入对象到指定集合
def insert_object(obj: BaseModel, collection_name: str, db_name: str = "rag", db_pool=None) -> Tuple[Union[None, str], Union[str, None]]:
    try:
        obj_dict = obj.dict()  # Pydantic 对象转为字典
        obj_dict['_id'] = obj.id  # 假设 Pydantic 类中有 'id' 字段作为唯一标识

        # 插入主表数据
        ok, res = insert_data(db_name, collection_name, obj_dict, db_pool=db_pool)
        if not ok:
            return f"插入对象到数据库失败: {res}", None

        return None, res
    except Exception as e:
        return f"插入对象到数据库时出错: {str(e)}", None


# 查：根据 ID 获取对象
def get_object_by_id(object_id: str, obj_class: Type[BaseModel], collection_name: str, db_name: str = "rag", db_pool=None) -> Tuple[Union[None, str], Union[BaseModel, None]]:
    try:
        # 从 MongoDB 获取数据
        ok, res = get_data_by_id(db_name, collection_name, object_id, db_pool=db_pool)
        if not ok:
            return f"查询数据库失败: {res}", None

        # 转换为 Pydantic 对象
        sw, obj = _get_object_from_res(res, obj_class)
        if sw:
            return sw, None

        return None, obj
    except Exception as e:
        return f"查询数据库时出错: {str(e)}", None


def get_objects_by_conditions(
        conditions: dict,
        obj_class: Type[BaseModel],
        collection_name: str,
        db_name: str = "rag",
        db_pool=None,
        limit: int = 0
) -> Tuple[Union[None, str], Union[List[BaseModel], None]]:
    try:
        # 如果 limit 大于 0，表示需要限制返回的数量
        query_limit = limit if limit > 0 else 0

        # 查询符合条件的对象
        ok, res = find_objects(db_name, collection_name, conditions, db_pool=db_pool, limit=query_limit)
        if not ok:
            return f"根据条件查询对象失败: {res}", None

        # 转换为 Pydantic 对象列表
        objects = []
        for raw_obj in res:
            sw, obj = _get_object_from_res(raw_obj, obj_class)
            if sw:
                return sw, None
            objects.append(obj)

        return None, objects
    except Exception as e:
        return f"根据条件查询对象时出错: {str(e)}", None


# 更新：根据对象ID更新指定集合中的对象
def update_object(
        object_id: str,  # 更新对象的 ID
        obj: BaseModel,  # 更新的 Pydantic 对象
        collection_name: str,  # 集合名称
        db_name: str = "rag",  # 数据库名称
        db_pool=None  # 数据库连接池
) -> Tuple[Union[None, str], Union[str, None]]:
    try:
        # 将对象转换为字典形式
        obj_dict = obj.dict(exclude_unset=True)  # exclude_unset=True 忽略没有修改的字段
        if '_id' in obj_dict:
            del obj_dict['_id']  # 删除 '_id' 字段，MongoDB 会自动处理此字段

        # 使用现有的 update_data_by_id 函数进行更新
        ok, res = update_data_by_id(db_name, collection_name, object_id, obj_dict, db_pool=db_pool)
        if not ok:
            return f"更新对象到数据库失败: {res}", None

        return None, res
    except Exception as e:
        return f"更新对象到数据库时出错: {str(e)}", None


def delete_object(
        object_id: str,
        collection_name: str,
        db_name: str = "rag",
        db_pool=None
) -> Tuple[Union[None, str], Union[str, None]]:
    try:
        # 调用 delete_data_by_id 删除指定 ID 的对象
        ok, res = delete_data_by_id(db_name, collection_name, object_id)
        if not ok:
            return f"删除对象失败: {res}", None

        return None, res
    except Exception as e:
        return f"删除对象时出错: {str(e)}", None
