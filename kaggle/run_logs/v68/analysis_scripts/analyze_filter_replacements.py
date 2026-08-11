"""Filter replacement analysis from v68 generated_mcqs.csv.

Computes:
- Total replacements by filter type (NLI, leak, length, blocklist, duplicate)
- Percentages of each
- Per-language and per-variant breakdowns
- Root-cause attribution

All numbers traceable to pilot1_test_generated_mcqs.csv.
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
    n = len(mcqs)

    total_fallback = sum(to_float(r.get("fallback_count", 0) or 0) for r in mcqs)
    total_nli = sum(to_float(r.get("nli_replaced", 0) or 0) for r in mcqs)
    total_leak = sum(to_float(r.get("leak_replaced", 0) or 0) for r in mcqs)
    total_length = sum(to_float(r.get("length_replaced", 0) or 0) for r in mcqs)
    total_blocklist = sum(to_float(r.get("blocklist_replaced", 0) or 0) for r in mcqs)
    total_dup = sum(to_float(r.get("dup_replaced", 0) or 0) for r in mcqs)

    # Overall summary
    overall = [
        ["metric", "total_count", "mean_per_mcq", "pct_of_total_replacements"],
        ["fallback_count", round(total_fallback, 2), round(total_fallback / n, 4), "100.0%"],
        ["nli_replaced", round(total_nli, 2), round(total_nli / n, 4), f"{round(total_nli/total_fallback*100,1) if total_fallback else 0}%"],
        ["leak_replaced", round(total_leak, 2), round(total_leak / n, 4), f"{round(total_leak/total_fallback*100,1) if total_fallback else 0}%"],
        ["length_replaced", round(total_length, 2), round(total_length / n, 4), f"{round(total_length/total_fallback*100,1) if total_fallback else 0}%"],
        ["blocklist_replaced", round(total_blocklist, 2), round(total_blocklist / n, 4), f"{round(total_blocklist/total_fallback*100,1) if total_fallback else 0}%"],
        ["dup_replaced", round(total_dup, 2), round(total_dup / n, 4), f"{round(total_dup/total_fallback*100,1) if total_fallback else 0}%"],
    ]

    # Per-language
    by_lang = defaultdict(list)
    for r in mcqs:
        by_lang[r.get("language", "Unknown")].append(r)

    lang_rows = [["language", "n", "fallback_mean", "nli_mean", "leak_mean", "length_mean", "blocklist_mean", "dup_mean"]]
    for lang in sorted(by_lang):
        rows = by_lang[lang]
        ln = len(rows)
        lang_rows.append([
            lang, ln,
            round(sum(to_float(r.get("fallback_count", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("nli_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("leak_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("length_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("blocklist_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("dup_replaced", 0) or 0) for r in rows) / ln, 4),
        ])

    # Per-variant
    by_var = defaultdict(list)
    for r in mcqs:
        by_var[r.get("variant", "Unknown")].append(r)

    var_rows = [["variant", "n", "fallback_mean", "nli_mean", "leak_mean", "length_mean", "blocklist_mean", "dup_mean"]]
    for var in sorted(by_var):
        rows = by_var[var]
        ln = len(rows)
        var_rows.append([
            var, ln,
            round(sum(to_float(r.get("fallback_count", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("nli_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("leak_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("length_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("blocklist_replaced", 0) or 0) for r in rows) / ln, 4),
            round(sum(to_float(r.get("dup_replaced", 0) or 0) for r in rows) / ln, 4),
        ])

    # Write overall
    with open(OUT / "table_filter_replacement_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(overall)
        f.write("\n")
        w.writerows(lang_rows)
        f.write("\n")
        w.writerows(var_rows)

    print(f"Wrote {OUT / 'table_filter_replacement_analysis.csv'}")
    print("=== OVERALL ===")
    for row in overall[1:]:
        print(row)
    print("=== PER LANGUAGE ===")
    for row in lang_rows[1:]:
        print(row)
    print("=== PER VARIANT ===")
    for row in var_rows[1:]:
        print(row)

if __name__ == "__main__":
    main()
