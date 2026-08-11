#!/usr/bin/env python3
"""
Quick standalone metrics for the v69 Kaggle run.

Does not require v68 data. Reads:
    kaggle_run_logs/v69/openrouter_pilot1_test_output/
        pilot1_test_generated_mcqs.csv
        pilot1_test_audit_results.csv
        pilot1_test_summary.json

Outputs:
    kaggle_run_logs/v69/v69_quick_metrics.json
    kaggle_run_logs/v69/v69_quick_metrics.txt   (human-readable markdown)
    kaggle_run_logs/v69/fig_v69_status_distribution.png
    kaggle_run_logs/v69/fig_v69_replacement_breakdown.png
    kaggle_run_logs/v69/fig_v69_consensus_by_language.png

Usage:
    python kaggle_run_logs/v69/v69_quick_metrics.py
    python kaggle_run_logs/v69/v69_quick_metrics.py --run-dir path/to/output --out-dir path/to/output
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quick v69 standalone metrics.")
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def load(run_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    gen = pd.read_csv(run_dir / "pilot1_test_generated_mcqs.csv", encoding="utf-8-sig")
    audit = pd.read_csv(run_dir / "pilot1_test_audit_results.csv", encoding="utf-8-sig")
    with open(run_dir / "pilot1_test_summary.json", "r", encoding="utf-8") as fh:
        summary = json.load(fh)
    return gen, audit, summary


def compute(run_dir: Path) -> Dict[str, object]:
    gen, audit, summary = load(run_dir)
    merged = audit.merge(gen, on="mcq_id", how="left", suffixes=("", "_gen"))

    n = len(merged)
    perfect = (merged["consensus_frac"] == 1.0).sum()
    hcw = ((merged["consensus_frac"] >= 0.75) & (merged["consensus_correct"] == 0)).sum()
    correct = int(merged["consensus_correct"].sum())
    partial = (merged["generation_status"] == "partial").sum()
    length_fb = (merged["generation_status"] == "length_fallback").sum()
    parse_fb = (merged["generation_status"] == "parse_fallback").sum()

    result = {
        "n_mcqs": n,
        "cost_usd": summary.get("estimated_cost_usd", np.nan),
        "perfect_consensus_rate": perfect / n if n else np.nan,
        "hcw_rate": hcw / n if n else np.nan,
        "consensus_accuracy": correct / n if n else np.nan,
        "partial_plus_fallback_rate": (partial + length_fb) / n if n else np.nan,
        "hard_fallback_rate": length_fb / n if n else np.nan,
        "parse_fallback_rate": parse_fb / n if n else np.nan,
        "mean_fallback_count": float(merged["fallback_count"].mean()),
        "mean_nli_replaced": float(merged["nli_replaced"].mean()),
        "mean_leak_replaced": float(merged["leak_replaced"].mean()),
        "mean_length_replaced": float(merged["length_replaced"].mean()),
        "duplicate_options": int(gen["duplicate_options"].sum()) if "duplicate_options" in gen.columns else 0,
        "per_language": {},
        "per_variant": {},
        "per_generator": {},
    }

    for lang, g in merged.groupby("language"):
        ln = len(g)
        k = int(g["consensus_correct"].sum())
        result["per_language"][lang] = {
            "n": ln,
            "consensus_accuracy": k / ln if ln else np.nan,
            "accuracy_wilson_ci": wilson_ci(k, ln),
            "perfect_consensus_rate": (g["consensus_frac"] == 1.0).mean(),
            "hcw_rate": ((g["consensus_frac"] >= 0.75) & (g["consensus_correct"] == 0)).mean(),
            "partial_plus_fallback_rate": ((g["generation_status"].isin(["partial", "length_fallback"])).sum()) / ln if ln else np.nan,
            "mean_fallback_count": float(g["fallback_count"].mean()),
        }

    for variant, g in merged.groupby("variant"):
        ln = len(g)
        result["per_variant"][variant] = {
            "n": ln,
            "consensus_accuracy": g["consensus_correct"].mean(),
            "hcw_rate": ((g["consensus_frac"] >= 0.75) & (g["consensus_correct"] == 0)).mean(),
            "partial_plus_fallback_rate": (g["generation_status"].isin(["partial", "length_fallback"])).mean(),
        }

    for gen_name, g in merged.groupby("generator_model"):
        ln = len(g)
        result["per_generator"][gen_name] = {
            "n": ln,
            "consensus_accuracy": g["consensus_correct"].mean(),
            "hcw_rate": ((g["consensus_frac"] >= 0.75) & (g["consensus_correct"] == 0)).mean(),
            "partial_plus_fallback_rate": (g["generation_status"].isin(["partial", "length_fallback"])).mean(),
        }

    return result


def plot_status_distribution(merged: pd.DataFrame, out_path: Path) -> None:
    status_counts = merged["generation_status"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    status_counts.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("v69 generation-status distribution")
    ax.set_xlabel("Status")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for i, v in enumerate(status_counts.values):
        ax.text(i, v, f"{v}\n({v/len(merged):.1%})", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_replacement_breakdown(merged: pd.DataFrame, out_path: Path) -> None:
    cols = ["length_replaced", "leak_replaced", "nli_replaced"]
    totals = [merged[c].sum() for c in cols]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([c.replace("_replaced", "").upper() for c in cols], totals, color=["#ff7f0e", "#2ca02c", "#d62728"])
    ax.set_title("v69 replacement driver totals")
    ax.set_ylabel("Total replacements")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_consensus_by_language(merged: pd.DataFrame, out_path: Path) -> None:
    rows = []
    for lang, g in merged.groupby("language"):
        rows.append({
            "language": lang,
            "accuracy": g["consensus_correct"].mean(),
            "hcw": ((g["consensus_frac"] >= 0.75) & (g["consensus_correct"] == 0)).mean(),
            "perfect": (g["consensus_frac"] == 1.0).mean(),
        })
    df = pd.DataFrame(rows).set_index("language").reindex(["English", "Arabic", "Yoruba"])
    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(kind="bar", ax=ax, color=["#2ca02c", "#d62728", "#1f77b4"])
    ax.set_title("v69 consensus metrics by language")
    ax.set_ylabel("Rate")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(["Accuracy", "HCW", "Perfect consensus"])
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def format_table(result: Dict[str, object]) -> str:
    lines = [
        "# v69 Quick Metrics",
        "",
        f"**MCQs:** {result['n_mcqs']}  ",
        f"**Cost:** ${result['cost_usd']:.4f}  ",
        "",
        "## Aggregate",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Perfect consensus | {result['perfect_consensus_rate']:.1%} |",
        f"| HCW (≥75% wrong) | {result['hcw_rate']:.1%} |",
        f"| Consensus accuracy | {result['consensus_accuracy']:.1%} |",
        f"| Partial + fallback | {result['partial_plus_fallback_rate']:.1%} |",
        f"| Hard fallback | {result['hard_fallback_rate']:.1%} |",
        f"| Parse fallback | {result['parse_fallback_rate']:.1%} |",
        f"| Mean fallback count | {result['mean_fallback_count']:.2f} |",
        f"| Mean NLI replaced | {result['mean_nli_replaced']:.2f} |",
        f"| Mean leak replaced | {result['mean_leak_replaced']:.2f} |",
        f"| Mean length replaced | {result['mean_length_replaced']:.2f} |",
        f"| Duplicate options | {result['duplicate_options']} |",
        "",
        "## Per-language",
        "",
        "| Language | n | Accuracy | Wilson 95% CI | Perfect | HCW | Partial+fallback | Mean fallback |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for lang in ["English", "Arabic", "Yoruba"]:
        d = result["per_language"].get(lang, {})
        lo, hi = d.get("accuracy_wilson_ci", (0.0, 0.0))
        lines.append(
            f"| {lang} | {d.get('n', 0)} | {d.get('consensus_accuracy', 0):.1%} | "
            f"{lo:.1%}-{hi:.1%} | {d.get('perfect_consensus_rate', 0):.1%} | "
            f"{d.get('hcw_rate', 0):.1%} | {d.get('partial_plus_fallback_rate', 0):.1%} | "
            f"{d.get('mean_fallback_count', 0):.2f} |"
        )
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(
        f"- HCW <10%: {'PASS' if result['hcw_rate'] < 0.10 else 'FAIL'} ({result['hcw_rate']:.1%})"
    )
    lines.append(
        f"- Partial+fallback <15%: {'PASS' if result['partial_plus_fallback_rate'] < 0.15 else 'FAIL'} ({result['partial_plus_fallback_rate']:.1%})"
    )
    lines.append(
        f"- Cost <$1.50: {'PASS' if result['cost_usd'] < 1.50 else 'FAIL'} (${result['cost_usd']:.4f})"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    run_dir = args.run_dir or root / "openrouter_pilot1_test_output"
    out_dir = args.out_dir or root
    out_dir.mkdir(parents=True, exist_ok=True)

    if not run_dir.exists():
        print(f"v69 run directory not found: {run_dir}", file=sys.stderr)
        return 1

    result = compute(run_dir)

    # JSON output.
    json_path = out_dir / "v69_quick_metrics.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=float)

    # Text/markdown output.
    txt_path = out_dir / "v69_quick_metrics.txt"
    txt_path.write_text(format_table(result), encoding="utf-8")

    # Plots.
    if not args.no_plots:
        try:
            gen, audit, _ = load(run_dir)
            merged = audit.merge(gen, on="mcq_id", how="left", suffixes=("", "_gen"))
            plot_status_distribution(merged, out_dir / "fig_v69_status_distribution.png")
            plot_replacement_breakdown(merged, out_dir / "fig_v69_replacement_breakdown.png")
            plot_consensus_by_language(merged, out_dir / "fig_v69_consensus_by_language.png")
        except Exception as exc:
            print(f"Plot generation failed: {exc}", file=sys.stderr)

    print(f"Quick metrics written to {json_path} and {txt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
