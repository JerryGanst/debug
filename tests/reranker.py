from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# 选择合适的 BGE ReRanker
# reranker_model = "BAAI/bge-reranker-large"  # 可替换为 base 或 small
reranker_model = "BAAI/bge-reranker-base"  # 可替换为 base 或 small
# reranker_model = "BAAI/bge-reranker-small"  # 可替换为 base 或 small
tokenizer = AutoTokenizer.from_pretrained(reranker_model)
model = AutoModelForSequenceClassification.from_pretrained(reranker_model)


def rerank(query, documents):
    inputs = tokenizer([query + " [SEP] " + doc for doc in documents], padding=True, truncation=True,
                       return_tensors="pt")
    with torch.no_grad():
        scores = model(**inputs).logits.squeeze().tolist()

    # 按分数降序排序
    reranked_docs = [doc for _, doc in sorted(zip(scores, documents), reverse=True)]
    return reranked_docs


# 示例 Query 和 文档
query = "什么是量子纠缠？"
documents = [
    "量子纠缠是一种物理现象，它发生在...",
    "量子计算依赖于量子比特和纠缠态...",
    "在经典物理学中，粒子没有量子纠缠这种特性..."
]

if __name__ == "__main__":
    # 进行 ReRanking
    reranked_results = rerank(query, documents)
    print("重新排序后的文档：", reranked_results)
