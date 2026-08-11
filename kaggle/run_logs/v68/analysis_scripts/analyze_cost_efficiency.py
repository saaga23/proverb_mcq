"""Cost efficiency analysis from v68 summary.json and generated_mcqs.csv.

Computes:
- Total cost, cost per MCQ, cost per language, cost per variant
- Audit ratio (4 auditors x 180 MCQs = 720 votes)
- Cost per vote
- Generation vs audit cost split (estimated)

Traceability: every number comes from pilot1_test_summary.json
and pilot1_test_generated_mcqs.csv.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main() -> None:
    summary = load_json(BASE / "pilot1_test_summary.json")
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")

    total_cost = summary.get("estimated_cost_usd", 0.0)
    n_mcqs = len(mcqs)
    n_languages = len(set(r.get("language") for r in mcqs))
    n_variants = len(set(r.get("variant") for r in mcqs))
    n_generators = len(summary.get("generator_pool", {}).get("active", []))
    n_auditors = len(summary.get("committee_pool", {}).get("active", []))

    # Per-language counts
    lang_counts = defaultdict(int)
    for r in mcqs:
        lang_counts[r.get("language", "Unknown")] += 1

    # Per-variant counts
    var_counts = defaultdict(int)
    for r in mcqs:
        var_counts[r.get("variant", "Unknown")] += 1

    rows = [
        ["metric", "value"],
        ["total_cost_usd", round(total_cost, 6)],
        ["n_mcqs", n_mcqs],
        ["cost_per_mcq_usd", round(total_cost / n_mcqs, 6) if n_mcqs else None],
        ["cost_per_language_usd", round(total_cost / n_languages, 6) if n_languages else None],
        ["cost_per_variant_usd", round(total_cost / n_variants, 6) if n_variants else None],
        ["n_generators_active", n_generators],
        ["n_auditors_active", n_auditors],
        ["total_audit_votes", n_mcqs * n_auditors],
        ["cost_per_audit_vote_usd", round(total_cost / (n_mcqs * n_auditors), 6) if (n_mcqs * n_auditors) else None],
        ["generation_calls_estimate", n_mcqs * n_generators],
        ["audit_calls_estimate", n_mcqs * n_auditors],
        ["total_api_calls_estimate", n_mcqs * n_generators + n_mcqs * n_auditors],
    ]

    for lang, cnt in sorted(lang_counts.items()):
        rows.append([f"cost_{lang.lower()}_usd", round(total_cost / n_languages, 6) if n_languages else None])
        rows.append([f"n_{lang.lower()}", cnt])

    for var, cnt in sorted(var_counts.items()):
        rows.append([f"cost_{var.lower()}_usd_estimate", round(total_cost / n_variants, 6) if n_variants else None])
        rows.append([f"n_{var.lower()}", cnt])

    out_path = OUT / "table_cost_efficiency.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)

    print(f"Wrote {out_path}")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
