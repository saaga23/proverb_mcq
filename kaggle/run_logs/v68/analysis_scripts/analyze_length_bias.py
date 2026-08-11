"""Length-bias analysis from v68 data.

Computes:
1. Mean option length by position (A/B/C/D)
2. Mean option length for consensus-correct vs consensus-wrong items
3. Correlation between length deviation and consensus selection

Traceability: pilot1_test_generated_mcqs.csv + pilot1_test_audit_results.csv
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def text_len(text: str) -> int:
    return len(text.strip())

def pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n == 0:
        return float("nan")
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)

def main() -> None:
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")
    audit = load_csv(BASE / "pilot1_test_audit_results.csv")
    audit_by_mcq = {r["mcq_id"]: r for r in audit}

    merged = []
    for m in mcqs:
        a = audit_by_mcq.get(m["mcq_id"])
        if a:
            m.update(a)
            merged.append(m)

    # 1. Mean length by position
    pos_lengths = defaultdict(list)
    for r in merged:
        label = r.get("correct_label", "").strip().upper()
        if label in ("A", "B", "C", "D"):
            pos_lengths[label].append(text_len(r.get(f"option_{label}", "")))
    
    pos_rows = [["position", "mean_length", "std_length", "n"]]
    for pos in ["A", "B", "C", "D"]:
        lens = pos_lengths[pos]
        if lens:
            mean = sum(lens) / len(lens)
            std = math.sqrt(sum((l - mean) ** 2 for l in lens) / len(lens))
            pos_rows.append([pos, round(mean, 2), round(std, 2), len(lens)])

    # 2. Length by consensus-correct vs consensus-wrong
    correct_lengths = []
    wrong_lengths = []
    for r in merged:
        label = r.get("correct_label", "").strip().upper()
        if label in ("A", "B", "C", "D"):
            length = text_len(r.get(f"option_{label}", ""))
            is_correct = str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true")
            if is_correct:
                correct_lengths.append(length)
            else:
                wrong_lengths.append(length)
    
    correct_mean = sum(correct_lengths) / len(correct_lengths) if correct_lengths else 0
    wrong_mean = sum(wrong_lengths) / len(wrong_lengths) if wrong_lengths else 0
    
    consensus_rows = [
        ["group", "mean_length", "std_length", "n"],
        ["consensus_correct", round(correct_mean, 2), round(math.sqrt(sum((l - correct_mean) ** 2 for l in correct_lengths) / len(correct_lengths)) if correct_lengths else 0, 2), len(correct_lengths)],
        ["consensus_wrong", round(wrong_mean, 2), round(math.sqrt(sum((l - wrong_mean) ** 2 for l in wrong_lengths) / len(wrong_lengths)) if wrong_lengths else 0, 2), len(wrong_lengths)],
    ]

    # 3. Correlation: for each option in each MCQ, is length correlated with being chosen?
    # We don't know which option was chosen by consensus, only whether the correct label was chosen.
    # Alternative: correlate mean distractor length with consensus-correct
    mean_distractor_lengths = []
    consensus_vec = []
    for r in merged:
        label = r.get("correct_label", "").strip().upper()
        if label not in ("A", "B", "C", "D"):
            continue
        correct_len = text_len(r.get(f"option_{label}", ""))
        distractor_lens = [text_len(r.get(f"option_{opt}", "")) for opt in ("A", "B", "C", "D") if opt != label]
        mean_distractor = sum(distractor_lens) / len(distractor_lens) if distractor_lens else 0
        mean_distractor_lengths.append(mean_distractor)
        consensus_vec.append(1 if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0)
    
    corr = pearson(mean_distractor_lengths, consensus_vec)
    correlation_rows = [
        ["metric", "value"],
        ["pearson_correlation_mean_distractor_length_vs_consensus_correct", round(corr, 4) if not math.isnan(corr) else "NaN"],
        ["n", len(mean_distractor_lengths)],
    ]

    # Write
    with open(OUT / "table_length_bias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(pos_rows)
        f.write("\n")
        w.writerows(consensus_rows)
        f.write("\n")
        w.writerows(correlation_rows)

    print(f"Wrote table_length_bias.csv")
    print("\n=== Mean length by position ===")
    for row in pos_rows[1:]:
        print(row)
    print("\n=== Consensus-correct vs consensus-wrong ===")
    for row in consensus_rows[1:]:
        print(row)
    print(f"\n=== Correlation ===")
    print(f"Pearson r (mean distractor length vs consensus-correct): {corr:.4f}")

if __name__ == "__main__":
    main()
