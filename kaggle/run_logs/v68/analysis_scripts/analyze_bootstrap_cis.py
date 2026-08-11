"""Bootstrap CIs for ALL v68 metrics.

Metrics:
- consensus_accuracy
- perfect_consensus_rate
- hcw_rate
- partial_or_fallback_rate
- hard_fallback_rate
- duplicate_rate
- per-language accuracy

10000 bootstrap samples.
Traceability: computed from pilot1_test_generated_mcqs.csv + pilot1_test_audit_results.csv
"""
from __future__ import annotations

import csv
import random
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def bootstrap_ci(values: list[float], n_bootstrap: int = 10000, alpha: float = 0.05) -> dict:
    random.seed(20260615)
    n = len(values)
    means = []
    for _ in range(n_bootstrap):
        sample = [random.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(alpha / 2 * n_bootstrap)]
    hi = means[int((1 - alpha / 2) * n_bootstrap)]
    point = sum(values) / n
    return {"point": round(point, 4), "ci_lower": round(lo, 4), "ci_upper": round(hi, 4), "n": n}

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

    # Overall metrics (binary vectors)
    consensus_correct_vec = [1 if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0 for r in merged]
    # perfect_consensus: consensus_frac == 1.0 (from audit)
    perfect_consensus_vec = [1 if float(r.get("consensus_frac", 0) or 0) >= 0.9999 else 0 for r in merged]
    # hcw: consensus_correct == 0
    hcw_vec = [1 if x == 0 else 0 for x in consensus_correct_vec]
    # partial_or_fallback
    partial_vec = [1 if r.get("generation_status", "") in ("partial", "length_fallback", "parse_fallback", "hard_fallback") else 0 for r in merged]
    # hard_fallback
    hard_vec = [1 if r.get("generation_status", "") == "hard_fallback" else 0 for r in merged]
    # duplicate
    dup_vec = [1 if str(r.get("duplicate_options", "0")).strip() in ("1", "True", "true") else 0 for r in merged]

    overall_metrics = {
        "consensus_accuracy": consensus_correct_vec,
        "perfect_consensus_rate": perfect_consensus_vec,
        "hcw_rate": hcw_vec,
        "partial_or_fallback_rate": partial_vec,
        "hard_fallback_rate": hard_vec,
        "duplicate_rate": dup_vec,
    }

    rows = [["metric", "point_estimate", "ci_lower_95", "ci_upper_95", "n"]]
    for name, vec in overall_metrics.items():
        ci = bootstrap_ci(vec)
        rows.append([name, ci["point"], ci["ci_lower"], ci["ci_upper"], ci["n"]])

    # Per-language consensus accuracy
    by_lang = defaultdict(list)
    for r in merged:
        by_lang[r.get("language", "Unknown")].append(r)

    for lang in ["English", "Arabic", "Yoruba"]:
        rows_lang = [r for r in by_lang[lang]]
        vec = [1 if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0 for r in rows_lang]
        ci = bootstrap_ci(vec)
        rows.append([f"consensus_accuracy_{lang}", ci["point"], ci["ci_lower"], ci["ci_upper"], ci["n"]])

    # Per-variant
    by_var = defaultdict(list)
    for r in merged:
        by_var[r.get("variant", "Unknown")].append(r)

    for var in sorted(by_var):
        rows_var = by_var[var]
        vec = [1 if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0 for r in rows_var]
        ci = bootstrap_ci(vec)
        rows.append([f"consensus_accuracy_{var}", ci["point"], ci["ci_lower"], ci["ci_upper"], ci["n"]])

    out_path = OUT / "table_bootstrap_cis.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)

    print(f"Wrote {out_path}")
    for row in rows[1:]:
        print(f"{row[0]:40s} {row[1]:.4f} [{row[2]:.4f}, {row[3]:.4f}] n={row[4]}")

if __name__ == "__main__":
    main()
