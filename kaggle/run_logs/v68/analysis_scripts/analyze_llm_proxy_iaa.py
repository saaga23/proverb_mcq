"""LLM-proxy IAA analysis from actual computed annotation data.

Reads iaa_report_20260708_121120.json (the ACTUAL computed report)
and produces a paper-ready CSV.

CRITICAL: Uses the ACTUAL computed Fleiss kappa = 0.4845,
NOT the previously claimed 0.6706. The 0.67 number was from
an earlier run with a different 3-model subset; the latest
computed value across all 7 models is 0.4845.

Traceability: every number comes from annotation/outputs/iaa_report_20260708_121120.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "openrouter_pilot1_test_output"
# Project root is 4 levels up from THIS file
IAA_DIR = Path(__file__).resolve().parents[4] / "annotation" / "outputs"
OUT = HERE.parent

def main() -> None:
    # Use the latest actual computed report
    report_path = IAA_DIR / "iaa_report_20260708_121120.json"
    if not report_path.exists():
        # Fallback to any iaa_report
        reports = sorted(IAA_DIR.glob("iaa_report_*.json"))
        if not reports:
            raise SystemExit("No IAA reports found in annotation/outputs/")
        report_path = reports[-1]
        print(f"Using fallback report: {report_path.name}")

    report = json.loads(report_path.read_text(encoding="utf-8"))

    rows = []
    # Header
    rows.append([
        "model", "n_total", "n_answered", "n_refusal",
        "acc_vs_consensus", "acc_vs_correct",
        "english_acc", "arabic_acc", "yoruba_acc"
    ])

    for m in report.get("per_model", []):
        per_lang = m.get("per_lang", {})
        rows.append([
            m.get("model", ""),
            m.get("n_total", 0),
            m.get("n_answered", 0),
            m.get("n_refusal", 0),
            m.get("acc_vs_consensus"),
            m.get("acc_vs_correct"),
            per_lang.get("English"),
            per_lang.get("Arabic"),
            per_lang.get("Yoruba"),
        ])

    # Summary stats
    pairwise = report.get("pairwise_cohen_kappa", {})
    kappa_values = list(pairwise.values())
    mean_pairwise_kappa = round(sum(kappa_values) / len(kappa_values), 4) if kappa_values else None
    min_pairwise_kappa = round(min(kappa_values), 4) if kappa_values else None
    max_pairwise_kappa = round(max(kappa_values), 4) if kappa_values else None
    fleiss = report.get("fleiss_kappa_all_models")

    # Write main table
    out_path = OUT / "table_llm_proxy_iaa.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)

        f.write("\n")
        f.write("=== SUMMARY STATISTICS ===\n")
        summary = [
            ["metric", "value"],
            ["fleiss_kappa_all_models", fleiss],
            ["mean_pairwise_cohen_kappa", mean_pairwise_kappa],
            ["min_pairwise_cohen_kappa", min_pairwise_kappa],
            ["max_pairwise_cohen_kappa", max_pairwise_kappa],
            ["n_models", len(report.get("per_model", []))],
            ["n_items", report.get("n_items")],
            ["source_report", report_path.name],
        ]
        w.writerows(summary)

    print(f"Wrote {out_path}")
    print(f"Source: {report_path.name}")
    print(f"Fleiss kappa: {fleiss}")
    print(f"Mean pairwise Cohen kappa: {mean_pairwise_kappa}")
    print("Per-model accuracy vs correct meaning:")
    for row in rows[1:]:
        print(f"  {row[0]:42s} acc_correct={row[5]}")

if __name__ == "__main__":
    main()
