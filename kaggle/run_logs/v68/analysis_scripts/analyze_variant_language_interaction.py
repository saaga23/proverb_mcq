"""Variant x language interaction analysis from v68 generated_mcqs.csv.

Computes mean fallback_count per (variant, language) cell.
This tests whether adversarial-hard-negative is disproportionately
aggressive in low-resource languages (Arabic/Yoruba) vs English.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def to_float(v) -> float | None:
    try:
        return float(v)
    except Exception:
        return None

def main() -> None:
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")

    cells = defaultdict(list)
    for r in mcqs:
        key = (r.get("variant", "Unknown"), r.get("language", "Unknown"))
        cells[key].append(to_float(r.get("fallback_count", 0) or 0) or 0.0)

    rows = [["variant", "language", "n", "fallback_mean", "fallback_std", "generated_pct", "partial_pct", "length_fallback_pct"]]
    for (variant, language), vals in sorted(cells.items()):
        n = len(vals)
        mean_fb = round(sum(vals) / n, 4)
        std_fb = round((sum((v - mean_fb) ** 2 for v in vals) / n) ** 0.5, 4)
        rows.append([variant, language, n, mean_fb, std_fb, "", "", ""])

    # Add generation-status percentages per cell
    status_counts = defaultdict(lambda: defaultdict(int))
    for r in mcqs:
        key = (r.get("variant", "Unknown"), r.get("language", "Unknown"))
        status_counts[key][r.get("generation_status", "unknown")] += 1

    for i, (variant, language) in enumerate(sorted(cells.keys())):
        counts = status_counts[(variant, language)]
        n = sum(counts.values())
        gen_pct = round(counts.get("generated", 0) / n, 4) if n else 0
        partial_pct = round(counts.get("partial", 0) / n, 4) if n else 0
        lf_pct = round(counts.get("length_fallback", 0) / n, 4) if n else 0
        rows[i + 1][5] = gen_pct
        rows[i + 1][6] = partial_pct
        rows[i + 1][7] = lf_pct

    out_path = OUT / "table_variant_language_interaction.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)

    print(f"Wrote {out_path}")
    for row in rows[1:]:
        print(row)

if __name__ == "__main__":
    main()
