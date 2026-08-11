"""Heuristic baselines from v68 data.

Baselines:
1. All-A: always pick position A
2. All-D: always pick position D
3. Random: uniform random among A/B/C/D (1000 trials)
4. Shortest: always pick the shortest option
5. Longest: always pick the longest option

Traceability: pilot1_test_generated_mcqs.csv
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def text_len(text: str) -> int:
    return len(text.strip())

def main() -> None:
    random.seed(20260615)
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")

    rows = []
    
    for m in mcqs:
        correct_label = m.get("correct_label", "").strip().upper()
        if correct_label not in ("A", "B", "C", "D"):
            continue
        options = {opt: m.get(f"option_{opt}", "").strip() for opt in ("A", "B", "C", "D")}
        if any(not v for v in options.values()):
            continue
        
        lengths = {opt: text_len(text) for opt, text in options.items()}
        
        # All-A
        all_a = 1 if "A" == correct_label else 0
        # All-D
        all_d = 1 if "D" == correct_label else 0
        # Random (1000 trials)
        random_correct = sum(1 for _ in range(1000) if random.choice(["A","B","C","D"]) == correct_label) / 1000
        # Shortest
        shortest_opt = min(lengths, key=lengths.get)
        shortest = 1 if shortest_opt == correct_label else 0
        # Longest
        longest_opt = max(lengths, key=lengths.get)
        longest = 1 if longest_opt == correct_label else 0
        
        rows.append({
            "mcq_id": m.get("mcq_id", ""),
            "correct_label": correct_label,
            "all_a": all_a,
            "all_d": all_d,
            "random": random_correct,
            "shortest": shortest,
            "longest": longest,
        })
    
    n = len(rows)
    summary = [
        ["baseline", "accuracy", "ci_lower", "ci_upper", "n"],
        ["all_A", round(sum(r["all_a"] for r in rows) / n, 4), "", "", n],
        ["all_D", round(sum(r["all_d"] for r in rows) / n, 4), "", "", n],
        ["random", round(sum(r["random"] for r in rows) / n, 4), "", "", n],
        ["shortest", round(sum(r["shortest"] for r in rows) / n, 4), "", "", n],
        ["longest", round(sum(r["longest"] for r in rows) / n, 4), "", "", n],
    ]
    
    out_path = OUT / "table_heuristic_baselines.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(summary)
    
    print(f"Wrote {out_path}")
    for row in summary[1:]:
        print(f"{row[0]:15s} {row[1]:.4f}")

if __name__ == "__main__":
    main()
