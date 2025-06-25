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

def load_glossary(glossary_path: str | None = None) -> List[Tuple[str, str, str]]:
    if glossary_path:
        _path = Path(glossary_path)
    else:
        # project/utils/glossary.py → project/glossary.csv
        _path = Path(__file__).resolve().parent.parent / "glossary.csv"
    
    if not _path.exists():
        return []

    with _path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not {"en", "zh", "vi"}.issubset(reader.fieldnames or {}):
            raise ValueError("glossary.csv 必须包含列: en, zh, vi")
        return [
            (row["en"].strip(), row["zh"].strip(), row["vi"].strip())
            for row in reader
            if row["en"].strip() and row["zh"].strip() and row["vi"].strip()
        ]


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
