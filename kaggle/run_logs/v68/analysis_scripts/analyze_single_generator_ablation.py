"""Single-generator vs pooled ablation from v68 data.

Reads generated_mcqs.csv and audit_results.csv,
computes per-generator and pooled metrics.
All numbers traceable to v68 output CSVs.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # strip BOM from keys
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def compute_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {}
    consensus_correct = sum(1 for r in rows if str(r.get("consensus_correct", "")).strip() in ("1", "True", "true"))
    hcw = 0
    partial_fallback = 0
    perfect_consensus = 0
    for r in rows:
        status = str(r.get("generation_status", "")).strip()
        # HCW: consensus_correct == 0
        if str(r.get("consensus_correct", "")).strip() in ("0", "False", "false"):
            hcw += 1
        if status in ("partial", "length_fallback", "parse_fallback", "hard_fallback"):
            partial_fallback += 1
        if status == "generated":
            pass  # not partial/fallback
        # perfect consensus from audit_results: consensus_frac == 1.0
        # We'll compute this separately from audit_results
    return {
        "n": n,
        "consensus_accuracy": round(consensus_correct / n, 4) if n else None,
        "hcw_rate": round(hcw / n, 4) if n else None,
        "partial_or_fallback_rate": round(partial_fallback / n, 4) if n else None,
    }

def main() -> None:
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")
    audit = load_csv(BASE / "pilot1_test_audit_results.csv")

    # Index audit by mcq_id
    audit_by_mcq = {r["mcq_id"]: r for r in audit}

    # Merge
    merged = []
    for m in mcqs:
        a = audit_by_mcq.get(m["mcq_id"])
        if a:
            m.update(a)
            merged.append(m)

    if not merged:
        print("No merged rows. Check mcq_id alignment.")
        return

    # Per-generator
    by_gen = defaultdict(list)
    for r in merged:
        key = r.get("generator_model") or r.get("model") or "unknown"
        by_gen[key].append(r)

    results = []
    for gen, rows in sorted(by_gen.items()):
        metrics = compute_metrics(rows)
        metrics["group"] = gen
        results.append(metrics)

    # Pooled
    pooled = compute_metrics(merged)
    pooled["group"] = "POOLED (all 3 generators)"
    results.append(pooled)

    # Write
    out_path = OUT / "table_single_generator_ablation.csv"
    if results:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Wrote {out_path}")
        for r in results:
            print(r)
    else:
        print("No data computed.")

if __name__ == "__main__":
    main()
