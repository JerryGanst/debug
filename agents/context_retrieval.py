from typing import List
import requests
import os
import logging

from models.query import ContextSource
from domains.context import DomainContext

logger = logging.getLogger(__name__)

def retrieve_context(info_to_collect: List[str], question_category: int, config: dict, process_recorder=None):
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    # 生成查询的嵌入向量
    query_embeddings = []
    embedding_endpoint = config.get("embedding_endpoint")
    if not embedding_endpoint:
        logger.error("未配置 embedding_endpoint，无法生成嵌入向量。")
        return []
    for query in info_to_collect:
        params = {"text": query}
        try:
            response = requests.post(embedding_endpoint, params=params)
            embedding = response.json().get('embedding')
            if embedding is not None:
                query_embeddings.append(embedding)
            else:
                logger.warning(f"嵌入向量服务响应中缺少 'embedding' 字段: {response.text}")
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {str(e)}")
            continue

    # 构建检索过滤条件，使用领域配置中的文档类型
    filters = {
        "chunk_doc_type": domain_config.DOMAIN_DOC_TYPE,  # 使用配置的领域文档类型
        'contents': query_embeddings,
        'topK': 5
    }

    # 执行检索
    try:
        resp = requests.post(f"{config.get('weaviate_endpoint')}/v1/chunk/get_chunks", json=filters)
        res = resp.json()
    except Exception as e:
        logger.error(f"检索上下文失败: {str(e)}")
        return []

    # 处理检索结果
    retrieved_contexts = []
    existing_chunk_ids = set()

    for rr in res:
        if process_recorder:
            process_recorder.retrieved_contexts_all.append(rr)
        cur_query_contexts = []
        for r in rr:
            try:
                if r['id'] in existing_chunk_ids:
                    continue

                existing_chunk_ids.add(r['id'])
                cur_context_source = ContextSource(
                    document_id=r['document']['id'],
                    document_title=r['document']['title'],
                    page=r['page_num'],
                    text=r['chunk_text'],
                    score=r['distance']
                )
                cur_query_contexts.append(cur_context_source)
            except Exception as e:
                logger.error(f"处理检索结果有问题：\n{r}\n{e}")
        retrieved_contexts.append(cur_query_contexts)

    # 扁平化结果列表
    return [item for sublist in retrieved_contexts for item in sublist]
