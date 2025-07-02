import random
import time
import requests
import pandas as pd
import re
from rapidfuzz import fuzz
from typing import List

# === 配置项 ===
CSV_PATH = "E:/luxshare-ai-rag/utils/glossary/glossary.csv"
TRANSLATE_URL = "http://localhost:9005/translate"
NUM_ITERATIONS = 50
USER_ID = "test-user"

# === 文本归一化处理 ===
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # 去标点
    text = re.sub(r'\b(a|an|the)\b', '', text)  # 去冠词
    text = re.sub(r'\s+', ' ', text)  # 多空格压缩
    return text.strip()

# === F1 分数计算 ===
def compute_f1(pred: str, ref: str) -> float:
    pred_tokens = normalize_text(pred).split()
    ref_tokens = normalize_text(ref).split()
    if not pred_tokens or not ref_tokens:
        return 0.0
    overlap = set(pred_tokens) & set(ref_tokens)
    if not overlap:
        return 0.0
    precision = len(overlap) / len(pred_tokens)
    recall = len(overlap) / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)

# === 加载词汇表 CSV ===
df = pd.read_csv(CSV_PATH)
assert "zh" in df.columns and "vi" in df.columns, "CSV 文件必须包含 'zh' 和 'vi' 列"

# === 开始测试 ===
f1_scores: List[float] = []
fail_count = 0
detailed_results = []

for i in range(NUM_ITERATIONS):
    row = df.sample(n=1).iloc[0]
    zh_text = str(row["zh"]).strip()
    vi_ref = str(row["vi"]).strip()

    payload = {
        "user_id": USER_ID,
        "source_text": zh_text,
        "target_language": "越南语"
    }

    try:
        res = requests.post(TRANSLATE_URL, json=payload, timeout=15)
        res.raise_for_status()
        data = res.json()
        vi_pred = data.get("translation_result", "").strip()
    except Exception as e:
        print(f"[{i+1}] ❌ 请求失败: {e}")
        print("     请求文本:", zh_text)
        print("     状态码:", getattr(res, 'status_code', 'N/A'))
        print("     响应:", getattr(res, 'text', '无响应'))
        fail_count += 1
        continue

    f1 = compute_f1(vi_pred, vi_ref)
    f1_scores.append(f1)
    detailed_results.append((zh_text, vi_ref, vi_pred, f1))

    print(f"[{i+1}] ✅ 测试项: {zh_text}")
    print(f"     参考译文: {vi_ref}")
    print(f"     实际输出: {vi_pred}")
    print(f"     F1 分数: {f1:.2f}\n")
    time.sleep(0.3)  # 节流

# === 结果汇总 ===
print("\n===== ✅ 测试结果统计 =====")
print(f"总测试次数: {NUM_ITERATIONS}")
print(f"成功翻译: {len(f1_scores)}")
print(f"失败请求: {fail_count}")
if f1_scores:
    avg_f1 = sum(f1_scores) / len(f1_scores)
    print(f"平均 F1 分数: {avg_f1:.4f}")
    # 找出最佳和最差翻译
    best_idx = f1_scores.index(max(f1_scores))
    worst_idx = f1_scores.index(min(f1_scores))
    print("\n--- 最佳样本 ---")
    print(f"中文: {detailed_results[best_idx][0]}")
    print(f"参考: {detailed_results[best_idx][1]}")
    print(f"翻译: {detailed_results[best_idx][2]}")
    print(f"F1: {detailed_results[best_idx][3]:.2f}")
    print("\n--- 最差样本 ---")
    print(f"中文: {detailed_results[worst_idx][0]}")
    print(f"参考: {detailed_results[worst_idx][1]}")
    print(f"翻译: {detailed_results[worst_idx][2]}")
    print(f"F1: {detailed_results[worst_idx][3]:.2f}")
else:
    print("❌ 无有效翻译结果")

