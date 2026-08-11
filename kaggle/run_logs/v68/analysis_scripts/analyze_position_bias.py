"""Position-bias analysis from v68 data.

Computes:
1. Position-bias chi-square: for each position A/B/C/D, count
   consensus-correct vs consensus-wrong. Run chi-square.
2. Position-corrected consensus metric: average accuracy across
   positions equally weighted.
3. Committee family diversity table.

Traceability: pilot1_test_generated_mcqs.csv + pilot1_test_audit_results.csv
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def chi_square_1d(observed: list[int]) -> dict:
    """Chi-square goodness-of-fit test for equal distribution."""
    n = sum(observed)
    if n == 0:
        return {"statistic": 0.0, "p_value": 1.0, "df": 0}
    expected = [n / len(observed)] * len(observed)
    stat = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
    try:
        from scipy.stats import chi2
        p = 1.0 - chi2.cdf(stat, len(observed) - 1)
        return {"statistic": round(float(stat), 4), "p_value": round(float(p), 6), "df": len(observed) - 1}
    except Exception:
        return {"statistic": round(float(stat), 4), "p_value": None, "df": len(observed) - 1, "note": "scipy not available"}

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

    # Position bias: for each position A/B/C/D, count consensus-correct vs consensus-wrong
    pos_correct = {"A": 0, "B": 0, "C": 0, "D": 0}
    pos_total = {"A": 0, "B": 0, "C": 0, "D": 0}
    pos_acc = {}
    for r in merged:
        correct_label = r.get("correct_label", "").strip().upper()
        consensus_correct = str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true")
        if correct_label in pos_correct:
            pos_total[correct_label] += 1
            if consensus_correct:
                pos_correct[correct_label] += 1

    for pos in ["A", "B", "C", "D"]:
        pos_acc[pos] = pos_correct[pos] / pos_total[pos] if pos_total[pos] else 0.0

    # Chi-square on position accuracies (observed correct counts)
    observed = [pos_correct[p] for p in ["A", "B", "C", "D"]]
    chi2_result = chi_square_1d(observed)

    # Position-corrected consensus: mean of per-position accuracies (unweighted)
    raw_consensus = sum(1 for r in merged if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true")) / len(merged)
    corrected_consensus = sum(pos_acc.values()) / 4

    pos_rows = [
        ["position", "correct", "total", "accuracy"],
        ["A", pos_correct["A"], pos_total["A"], round(pos_acc["A"], 4)],
        ["B", pos_correct["B"], pos_total["B"], round(pos_acc["B"], 4)],
        ["C", pos_correct["C"], pos_total["C"], round(pos_acc["C"], 4)],
        ["D", pos_correct["D"], pos_total["D"], round(pos_acc["D"], 4)],
        ["ALL", sum(observed), sum(pos_total.values()), round(raw_consensus, 4)],
        ["CORRECTED", "", "", round(corrected_consensus, 4)],
    ]

    # Committee family diversity
    family_map = {
        "meta-llama/llama-3.3-70b-instruct": "Meta",
        "mistralai/mistral-small-3.2-24b-instruct": "Mistral",
        "google/gemma-3-27b-it": "Google",
        "deepseek/deepseek-v3.2": "DeepSeek",
    }

    # We don't have per-auditor vote data in merged directly; use table_auditor_vs_gold
    # Instead, map generators to families
    gen_family = {
        "qwen/qwen3.7-max": "Qwen",
        "google/gemma-4-31b-it": "Google",
        "google/gemini-2.5-flash": "Google",
    }

    family_rows = [["role", "family", "model", "accuracy_vs_gold"]]
    # From auditor vs gold table
    gold_table = load_csv(OUT / "table_auditor_vs_gold.csv")
    for row in gold_table:
        auditor_name = row.get("auditor", "")
        if not auditor_name or auditor_name in ["auditor", "metric"]:
            continue
        model = auditor_name
        family = "Unknown"
        for k, v in family_map.items():
            if k.replace("/", "_") in model:
                family = v
                break
        family_rows.append(["auditor", family, model, row.get("accuracy_vs_gold", "")])

    # Generator families
    gen_rows = [["generator_model", "family", "consensus_accuracy", "hcw_rate", "partial_or_fallback_rate"]]
    by_gen = defaultdict(list)
    for r in merged:
        by_gen[r.get("generator_model", "unknown")].append(r)
    for gen, rows in sorted(by_gen.items()):
        acc = sum(1 for r in rows if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true")) / len(rows)
        hcw = sum(1 for r in rows if str(r.get("consensus_correct", "0")).strip() in ("0", "False", "false")) / len(rows)
        partial = sum(1 for r in rows if r.get("generation_status", "") in ("partial", "length_fallback", "parse_fallback", "hard_fallback")) / len(rows)
        family = gen_family.get(gen, "Unknown")
        gen_rows.append([gen, family, round(acc, 4), round(hcw, 4), round(partial, 4)])

    # Write
    with open(OUT / "table_position_bias_chi2.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(pos_rows)
        f.write("\n")
        w.writerows([["chi2_statistic", chi2_result["statistic"], "p_value", chi2_result.get("p_value"), "df", chi2_result.get("df")]])
        f.write("\n")
        w.writerows([["position_corrected_consensus", round(corrected_consensus, 4), "raw_consensus", round(raw_consensus, 4), "delta", round(corrected_consensus - raw_consensus, 4)]])

    with open(OUT / "table_committee_family.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(family_rows)
        f.write("\n")
        w.writerows(gen_rows)

    print(f"Wrote table_position_bias_chi2.csv")
    print(f"Wrote table_committee_family.csv")
    print("\n=== Position Bias ===")
    for row in pos_rows:
        print(row)
    print(f"\nChi-square: {chi2_result}")
    print(f"Raw consensus accuracy: {raw_consensus:.4f}")
    print(f"Position-corrected consensus: {corrected_consensus:.4f}")
    print(f"Delta (corrected - raw): {corrected_consensus - raw_consensus:.4f}")

if __name__ == "__main__":
    main()
