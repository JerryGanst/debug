import csv
from pathlib import Path
from typing import List, Tuple

from rapidfuzz import fuzz

FUZZ_THRESHOLD = 80
TOP_K_TERMS = 50

def glossary_extract(source_text: str, glossary_path: str | None = None) -> str:
    glossary = load_glossary(glossary_path)
    lines = extract_related(source_text, glossary)
    return "\n".join(f"- {line}" for line in lines)

def safe_strip(val: str | None) -> str:
    return val.strip() if isinstance(val, str) else ""

def load_glossary(glossary_path: str | None = None) -> List[Tuple[str, str, str]]:
    if glossary_path:
        _path = Path(glossary_path)
    else:
        _path = Path(__file__).resolve().parent / "glossary.csv"
    
    if not _path.exists():
        return []

    with _path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not {"en", "zh", "vi"}.issubset(reader.fieldnames or {}):
            raise ValueError("glossary.csv 必须包含列: en, zh, vi")

        glossary: List[Tuple[str, str, str]] = []
        for i, row in enumerate(reader, start=2):  # start=2 跳过表头
            en = safe_strip(row.get("en"))
            zh = safe_strip(row.get("zh"))
            vi = safe_strip(row.get("vi"))

            # 至少两个字段非空才保留
            if sum(bool(x) for x in (en, zh, vi)) >= 2:
                glossary.append((en, zh, vi))
            else:
                print(f"[WARN] 第{i}行跳过（非空列不足2）：{row}")

    return glossary



def extract_related(
    source_text: str,
    glossary: List[Tuple[str, str, str]],
    *,
    threshold: int = FUZZ_THRESHOLD,
    top_k: int = TOP_K_TERMS,
) -> List[str]:
    if not glossary:
        return []
    lower_text = source_text.lower()
    scored: List[Tuple[int, str]] = []
    for en, zh, vi in glossary:
        score = max(
            fuzz.partial_ratio(lower_text, en.lower()),
            fuzz.partial_ratio(lower_text, zh.lower()),
            fuzz.partial_ratio(lower_text, vi.lower()),
        )
        if score >= threshold:
            scored.append((score, f"{en} <-> {zh} <-> {vi}"))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]

__all__ = [
    "glossary_extract",
    "load_glossary",
    "extract_related",
]
