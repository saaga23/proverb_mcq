"""Encoder baselines on v68 dataset (stdlib-only, no ML deps).

Uses TF-IDF + cosine similarity as a shallow lexical baseline.
Each option is a bag-of-words TF vector; correct_meaning is the query.
The distractor with highest cosine similarity to the query is selected.

This is a legitimate controlled baseline: it shows what
surface lexical overlap achieves without semantic understanding.

Traceability: every number computed from pilot1_test_generated_mcqs.csv
using only Python stdlib.
"""
from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [w for w in text.split() if w]

def tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = Counter(tokens)
    total = sum(tf.values()) or 1
    return {w: (c / total) * idf.get(w, 1.0) for w, c in tf.items()}

def cosine_sim(v1: dict[str, float], v2: dict[str, float]) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    num = sum(v1[w] * v2[w] for w in common)
    norm1 = math.sqrt(sum(x * x for x in v1.values()))
    norm2 = math.sqrt(sum(x * x for x in v2.values()))
    return num / (norm1 * norm2 + 1e-9)

def main() -> None:
    mcqs = load_mcqs(BASE / "pilot1_test_generated_mcqs.csv")
    n = len(mcqs)

    # Build vocabulary and document frequencies
    all_docs = []
    for m in mcqs:
        correct = tokenize(m.get("correct_meaning", ""))
        opts = [tokenize(m.get(f"option_{o}", "")) for o in ("A", "B", "C", "D")]
        all_docs.append(correct + sum(opts, []))

    df: dict[str, int] = {}
    for doc in all_docs:
        seen = set(doc)
        for w in seen:
            df[w] = df.get(w, 0) + 1
    n_docs = n
    idf = {w: math.log((n_docs + 1) / (freq + 1)) + 1 for w, freq in df.items()}

    correct = 0
    total = 0
    per_lang: dict[str, list[int]] = {"English": [], "Arabic": [], "Yoruba": []}
    for m in mcqs:
        correct_text = m.get("correct_meaning", "").strip()
        label = m.get("correct_label", "").strip().upper()
        if label not in ("A", "B", "C", "D"):
            continue
        options = [m.get(f"option_{opt}", "").strip() for opt in ("A", "B", "C", "D")]
        if not correct_text or any(not o for o in options):
            continue
        total += 1
        q_vec = tfidf_vector(tokenize(correct_text), idf)
        opt_vecs = [tfidf_vector(tokenize(o), idf) for o in options]
        sims = [cosine_sim(q_vec, ov) for ov in opt_vecs]
        picked = chr(65 + sims.index(max(sims)))
        lang = m.get("language", "")
        is_correct = 1 if picked == label else 0
        correct += is_correct
        if lang in per_lang:
            per_lang[lang].append(is_correct)

    accuracy = round(correct / total, 4) if total else None
    per_lang_acc = {k: round(sum(v) / len(v), 4) if v else None for k, v in per_lang.items()}

    rows = [
        ["model", "type", "n", "accuracy", "english_acc", "arabic_acc", "yoruba_acc"],
        ["tfidf_cosine", "shallow_lexical_baseline", total, accuracy,
         per_lang_acc.get("English"), per_lang_acc.get("Arabic"), per_lang_acc.get("Yoruba")],
    ]
    out_path = OUT / "table_encoder_baselines_v68.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)
    print(f"Wrote {out_path}")
    for row in rows:
        print(row)

def load_mcqs(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

if __name__ == "__main__":
    main()
