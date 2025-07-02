import random
import requests
import time

API_URL = "http://localhost:9005/translate"

from pathlib import Path

LOG_PATH = Path("structure_test_report.md")

def log_to_markdown(index, direction, source, reference, translated, s_score, c_score):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"## 样本 #{index:02d} | {direction}\n")
        f.write(f"- 结构保持率: `{s_score:.2f}`\n")
        f.write(f"- 内容完整率: `{c_score:.2f}`\n\n")
        f.write(f"### 🔹 原始输入（source_text）\n```markdown\n{source}\n```\n")
        f.write(f"### 🔸 参考译文结构（reference_markdown）\n```markdown\n{reference}\n```\n")
        f.write(f"### 🟡 实际翻译结果（translated）\n```markdown\n{translated}\n```\n")
        f.write("\n---\n\n")


# 模拟表格生成器
def generate_fake_markdown_table() -> str:
    num_cols = random.randint(2, 5)
    num_rows = random.randint(2, 8)

    # 构造表头
    headers = [f"列{i}" for i in range(1, num_cols + 1)]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * num_cols) + " |"

    # 构造数据行
    rows = []
    for _ in range(num_rows):
        row = []
        for _ in range(num_cols):
            choice = random.choice(["词", "123", "", "特别长的字段数据内容", "v1.0版本", "!!"])
            row.append(choice)
        rows.append("| " + " | ".join(row) + " |")

    return "\n".join([header_line, separator] + rows)

# 插入上下文模拟真实文档
def inject_context(table: str) -> str:
    pre = random.choice([
        "# 项目人员分布表", "以下是统计数据：", "## Monthly Report", "> 注意：数据来自2023年系统导出"
    ])
    post = random.choice([
        "", "备注：请仔细核对", "> 表格字段可能存在缺失", "注：以上数据已过期"
    ])
    return f"{pre}\n\n{table}\n\n{post}"

# 提取纯表格行
def extract_table_lines(text: str) -> list:
    return [line for line in text.split('\n') if "|" in line and "---" not in line or "—" in line]

# 结构评分：行列对齐
def structure_match_rate(src: str, tgt: str) -> float:
    src_lines = extract_table_lines(src)
    tgt_lines = extract_table_lines(tgt)
    if len(src_lines) != len(tgt_lines):
        return 0.0
    match = sum(1 for s, t in zip(src_lines, tgt_lines) if s.count("|") == t.count("|"))
    return match / len(src_lines) if src_lines else 1.0

# 内容评分：单元格完整性
def content_completion_rate(src: str, tgt: str) -> float:
    src_cells = sum(line.count("|") - 1 for line in extract_table_lines(src))
    tgt_cells = sum(line.count("|") - 1 for line in extract_table_lines(tgt))
    if src_cells == 0:
        return 1.0
    return min(tgt_cells / src_cells, 1.0)

# 调用翻译接口
def call_translate_api(source_text: str, target_lang: str) -> str:
    payload = {
        "user_id": "test_user",
        "target_language": target_lang,
        "source_text": source_text
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()["translation_result"]
    except Exception as e:
        print(f"[ERROR] 接口调用失败：{e}")
        return ""

# 主流程
def main(n=10):
    struct_scores, content_scores = [], []

    for i in range(1, n + 1):
        direction = random.choice(["中文→越南语", "越南语→中文"])
        source_lang = "中文" if "中文" in direction else "越南语"
        target_lang = "越南语" if source_lang == "中文" else "中文"

        # 原始表格构造
        raw_table = generate_fake_markdown_table()
        source_text = inject_context(raw_table)

        # 模拟参考翻译（结构一致，仅用于评分）
        reference_text = inject_context(raw_table.replace("列", "Tên" if target_lang == "越南语" else "字段"))

        translated = call_translate_api(source_text, target_lang)
        if not translated:
            continue

        s_score = structure_match_rate(reference_text, translated)
        c_score = content_completion_rate(reference_text, translated)

        struct_scores.append(s_score)
        content_scores.append(c_score)
        log_to_markdown(i, direction, source_text, reference_text, translated, s_score, c_score)

        print(f"#{i:02d} | {direction} | 结构评分: {s_score:.2f} | 内容评分: {c_score:.2f}")

        time.sleep(1.0)  # 稍作延迟，避免接口过载

    # 汇总结果
    print("\n======= 总结 =======")
    print(f"平均结构保持率：{sum(struct_scores) / len(struct_scores):.2f}")
    print(f"平均内容完整率：{sum(content_scores) / len(content_scores):.2f}")
    print(f"失败样本数量：{n - len(struct_scores)}")

if __name__ == "__main__":
    main()
