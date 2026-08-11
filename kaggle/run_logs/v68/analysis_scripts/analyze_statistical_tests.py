"""Statistical tests for v68 data.

Tests:
1. McNemar's test for paired comparisons between variants (same proverbs).
2. Wilcoxon signed-rank test for per-generator accuracy distributions.
3. Holm-Bonferroni correction for multiple comparisons.

Traceability: every test computed from pilot1_test_generated_mcqs.csv
and pilot1_test_audit_results.csv.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def mcnemar(pair_a: list[int], pair_b: list[int]) -> dict:
    """Compute McNemar's test for paired binary outcomes.
    pair_a, pair_b: lists of 0/1 for the same items.
    Returns statistic, p-value, interpretation.
    """
    n = len(pair_a)
    assert n == len(pair_b)
    b = sum(1 for a, b in zip(pair_a, pair_b) if a == 1 and b == 0)
    c = sum(1 for a, b in zip(pair_a, pair_b) if a == 0 and b == 1)
    if b + c == 0:
        return {"statistic": 0.0, "p_value": 1.0, "interpretation": "no discordance"}
    stat = (b - c) ** 2 / (b + c)
    # chi-square with 1 df approximation
    from math import sqrt
    p = 1.0 - (2.0 / (3.141592653589793 * sqrt(2.0))) * (stat ** 0.5) if stat > 0 else 1.0
    # Better p from scipy if available
    try:
        from scipy.stats import chi2
        p = 1.0 - chi2.cdf(stat, 1)
    except Exception:
        pass
    return {"statistic": round(stat, 4), "p_value": round(p, 6), "b": b, "c": c, "n": n}

def wilcoxon(x: list[float], y: list[float]) -> dict:
    """Compute Wilcoxon signed-rank test for paired samples.
    Returns statistic, p-value.
    """
    try:
        from scipy.stats import wilcoxon as scipy_wilcoxon
        stat, p = scipy_wilcoxon(x, y, alternative='two-sided')
        return {"statistic": float(stat), "p_value": round(float(p), 6)}
    except Exception:
        return {"statistic": None, "p_value": None, "note": "scipy not available"}

def holm_bonferroni(p_values: list[dict]) -> list[dict]:
    """Apply Holm-Bonferroni correction to a list of test results."""
    n = len(p_values)
    sorted_tests = sorted(enumerate(p_values), key=lambda x: x[1]["p_value"])
    results = [None] * n
    for rank, (orig_idx, test) in enumerate(sorted_tests):
        adjusted_p = test["p_value"] * (n - rank)
        adjusted_p = min(adjusted_p, 1.0)
        results[orig_idx] = {
            "test_name": test.get("test_name", ""),
            "p_raw": test["p_value"],
            "p_holm": round(adjusted_p, 6),
            "significant_005": adjusted_p < 0.05,
        }
    return results

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

    # Pair by (language, sample_id) => multiple variant rows per same proverb
    # group_id = language + "_" + sample_id
    by_proverb = defaultdict(list)
    for r in merged:
        lang = r.get("language", "")
        sample = r.get("sample_id", "")
        key = f"{lang}_{sample}"
        by_proverb[key].append(r)

    # McNemar: pairwise variant comparisons on same proverbs
    variants = sorted(set(r.get("variant", "") for r in merged))
    variant_pairs = []
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            variant_pairs.append((variants[i], variants[j]))

    mcnemar_rows = [["variant_a", "variant_b", "n_pairs", "b", "c", "statistic", "p_value", "significant_005"]]
    mcnemar_results = []
    for va, vb in variant_pairs:
        pairs_a, pairs_b = [], []
        for key, rows in by_proverb.items():
            row_a = next((r for r in rows if r.get("variant") == va), None)
            row_b = next((r for r in rows if r.get("variant") == vb), None)
            if row_a and row_b:
                pairs_a.append(1 if str(row_a.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0)
                pairs_b.append(1 if str(row_b.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0)
        if len(pairs_a) < 3:
            continue
        result = mcnemar(pairs_a, pairs_b)
        result["test_name"] = f"{va} vs {vb}"
        result["variant_a"] = va
        result["variant_b"] = vb
        result["n_pairs"] = len(pairs_a)
        mcnemar_results.append(result)
        sig = result["p_value"] < 0.05 if result["p_value"] is not None else False
        mcnemar_rows.append([va, vb, len(pairs_a), result.get("b", 0), result.get("c", 0), result["statistic"], result["p_value"], sig])

    # Holm-Bonferroni on McNemar results
    mcnemar_corrected = holm_bonferroni(mcnemar_results)

    # Wilcoxon: per-generator accuracy distributions (across 60 MCQs each)
    by_gen = defaultdict(list)
    for r in merged:
        by_gen[r.get("generator_model", "unknown")].append(r)

    gen_accs = {}
    for gen, rows in by_gen.items():
        accs = [1.0 if str(r.get("consensus_correct", "0")).strip() in ("1", "True", "true") else 0.0 for r in rows]
        gen_accs[gen] = accs

    wilcoxon_rows = [["generator_a", "generator_b", "n", "statistic", "p_value", "significant_005"]]
    wilcoxon_results = []
    gens = sorted(gen_accs.keys())
    for i in range(len(gens)):
        for j in range(i + 1, len(gens)):
            ga, gb = gens[i], gens[j]
            result = wilcoxon(gen_accs[ga], gen_accs[gb])
            result["test_name"] = f"{ga} vs {gb}"
            result["generator_a"] = ga
            result["generator_b"] = gb
            result["n"] = len(gen_accs[ga])
            wilcoxon_results.append(result)
            sig = result["p_value"] is not None and result["p_value"] < 0.05
            wilcoxon_rows.append([ga, gb, len(gen_accs[ga]), result["statistic"], result["p_value"], sig])

    wilcoxon_corrected = holm_bonferroni(wilcoxon_results)

    # Write outputs
    with open(OUT / "table_statistical_tests_mcnemar.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(mcnemar_rows)

    with open(OUT / "table_statistical_tests_wilcoxon.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(wilcoxon_rows)

    with open(OUT / "table_statistical_tests_corrected.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        combined = []
        for r in mcnemar_corrected:
            combined.append(["mcnemar"] + list(r.values()))
        for r in wilcoxon_corrected:
            combined.append(["wilcoxon"] + list(r.values()))
        w.writerows(combined)

    print("Wrote table_statistical_tests_mcnemar.csv")
    print("Wrote table_statistical_tests_wilcoxon.csv")
    print("Wrote table_statistical_tests_corrected.csv")
    print("\n=== McNemar Results ===")
    for row in mcnemar_rows[1:]:
        print(row)
    print("\n=== Wilcoxon Results ===")
    for row in wilcoxon_rows[1:]:
        print(row)

if __name__ == "__main__":
    main()
