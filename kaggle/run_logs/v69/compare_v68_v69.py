#!/usr/bin/env python3
"""
Statistical comparison of ProverbGap Pilot 1 TEST v68 (corpus fallback)
versus v69 (LLM fallback ablation).

Inputs (after both runs exist):
    kaggle_run_logs/v68/openrouter_pilot1_test_output/
        pilot1_test_generated_mcqs.csv
        pilot1_test_audit_results.csv
        pilot1_test_summary.json
    kaggle_run_logs/v69/openrouter_pilot1_test_output/
        pilot1_test_generated_mcqs.csv
        pilot1_test_audit_results.csv
        pilot1_test_summary.json

Outputs (written to kaggle_run_logs/v69/):
    v68_v69_comparison_table.csv
    v68_v69_paired_metrics.csv
    v68_v69_statistical_tests.csv
    v68_v69_per_language.csv
    v68_v69_per_variant.csv
    v68_v69_per_generator.csv
    fig_v68_v69_metric_bars.png
    fig_v68_v69_paired_scatter.png
    fig_v68_v69_delta_by_language.png
    v68_v69_comparison_report.md

Usage:
    python kaggle_run_logs/v69/compare_v68_v69.py
    python kaggle_run_logs/v69/compare_v68_v69.py --v69-dir path/to/v69 --out-dir path/to/output

The script is self-contained and only uses pandas + scipy + matplotlib + statsmodels.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.contingency_tables import mcnemar

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("compare_v68_v69")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONSENSUS_FRAC_STRONG = 0.75
PERFECT_CONSENSUS_FRAC = 1.0
COST_CAP_N5 = 1.50  # absolute cost guard for N=5
COST_CAP_N15_EST = 5.00  # extrapolated N=15 must stay under this

# User-specified go/no-go thresholds for v69 N=5.
GATES = {
    "hcw_rate": ("<", 0.10),
    "partial_plus_fallback_rate": ("<", 0.15),
    "perfect_consensus_rate": ("<", 0.30),  # informative but not part of strong pass
    "hard_fallback_rate": ("<", 0.05),
    "consensus_accuracy": (">=", 0.50),
    "duplicate_options_count": ("==", 0),
}

# Relative improvement thresholds v69 vs v68 (v69 should be *lower* for the
# first three and *higher* for consensus_accuracy).
RELATIVE_IMPROVEMENTS = {
    "hcw_rate": ("decrease", 0.20),
    "partial_plus_fallback_rate": ("decrease", 0.20),
    "perfect_consensus_rate": ("decrease", 0.10),
    "consensus_accuracy": ("increase", 0.05),
    "mean_fallback_count": ("decrease", 0.20),
}

REQUIRED_GEN_COLUMNS = {
    "mcq_id",
    "language",
    "sample_id",
    "generator_model",
    "variant",
    "generation_status",
    "fallback_count",
    "length_replaced",
    "leak_replaced",
    "nli_replaced",
    "duplicate_options",
    "correct_label",
}

REQUIRED_AUDIT_COLUMNS = {
    "mcq_id",
    "consensus_label",
    "consensus_frac",
    "consensus_correct",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare ProverbGap Pilot 1 TEST v68 (corpus fallback) vs v69 (LLM fallback)."
    )
    parser.add_argument(
        "--v68-dir",
        type=Path,
        default=None,
        help="Path to v68 openrouter_pilot1_test_output directory. Default: kaggle_run_logs/v68/openrouter_pilot1_test_output.",
    )
    parser.add_argument(
        "--v69-dir",
        type=Path,
        default=None,
        help="Path to v69 openrouter_pilot1_test_output directory. Default: kaggle_run_logs/v69/openrouter_pilot1_test_output.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for comparison artifacts. Default: directory containing this script.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip figure generation.",
    )
    return parser.parse_args()


def load_run(run_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load generated MCQs, audit results, and summary JSON for one run."""
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    gen_path = run_dir / "pilot1_test_generated_mcqs.csv"
    audit_path = run_dir / "pilot1_test_audit_results.csv"
    summary_path = run_dir / "pilot1_test_summary.json"

    missing = [p for p in [gen_path, audit_path, summary_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing expected files in {run_dir}: " + ", ".join(str(p) for p in missing)
        )

    gen = pd.read_csv(gen_path, encoding="utf-8-sig")
    audit = pd.read_csv(audit_path, encoding="utf-8-sig")

    gen_missing = REQUIRED_GEN_COLUMNS - set(gen.columns)
    audit_missing = REQUIRED_AUDIT_COLUMNS - set(audit.columns)
    if gen_missing:
        raise ValueError(f"Generated MCQs CSV missing columns: {sorted(gen_missing)}")
    if audit_missing:
        raise ValueError(f"Audit CSV missing columns: {sorted(audit_missing)}")

    with open(summary_path, "r", encoding="utf-8") as fh:
        summary = json.load(fh)

    return gen, audit, summary


def build_match_key(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a deterministic pairing key: language + sample_id + generator + variant.
    This matches the same proverb/variant/generator triplet across v68 and v69.
    """
    df = df.copy()
    df["match_key"] = (
        df["language"].astype(str).str.lower()
        + "::"
        + df["sample_id"].astype(str)
        + "::"
        + df["generator_model"].astype(str)
        + "::"
        + df["variant"].astype(str)
    )
    return df


def merge_run_data(gen: pd.DataFrame, audit: pd.DataFrame) -> pd.DataFrame:
    """Join generation metadata with audit outcomes on mcq_id."""
    gen = build_match_key(gen)

    # Audit results do not contain sample_id/proverb; map mcq_id to the
    # deterministic match key created from the generation file.
    audit = audit.copy()
    id_to_key = gen.set_index("mcq_id")["match_key"].to_dict()
    audit["match_key"] = audit["mcq_id"].map(id_to_key)

    # Use only the audit columns we need; avoid duplicating text columns.
    audit_cols = [
        "match_key",
        "mcq_id",
        "consensus_label",
        "consensus_frac",
        "consensus_correct",
    ]
    audit_cols += [c for c in audit.columns if c.startswith("vote_") or c.startswith("hit_")]
    audit_cols = list(dict.fromkeys(audit_cols))  # preserve order, remove dups

    merged = pd.merge(
        gen,
        audit[[c for c in audit_cols if c in audit.columns]],
        on="match_key",
        how="left",
        suffixes=("", "_audit"),
    )
    return merged


def derive_binary_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add binary outcome columns needed for paired tests."""
    df = df.copy()
    df["consensus_frac"] = pd.to_numeric(df["consensus_frac"], errors="coerce")
    df["consensus_correct"] = pd.to_numeric(df["consensus_correct"], errors="coerce").fillna(0).astype(int)
    df["fallback_count"] = pd.to_numeric(df["fallback_count"], errors="coerce").fillna(0)
    df["length_replaced"] = pd.to_numeric(df["length_replaced"], errors="coerce").fillna(0)
    df["leak_replaced"] = pd.to_numeric(df["leak_replaced"], errors="coerce").fillna(0)
    df["nli_replaced"] = pd.to_numeric(df["nli_replaced"], errors="coerce").fillna(0)

    df["perfect_consensus"] = (df["consensus_frac"] >= PERFECT_CONSENSUS_FRAC).astype(int)
    df["hcw"] = (
        (df["consensus_frac"] >= CONSENSUS_FRAC_STRONG) & (df["consensus_correct"] == 0)
    ).astype(int)
    df["partial_or_fallback"] = df["generation_status"].isin(
        ["partial", "length_fallback", "parse_fallback"]
    ).astype(int)
    df["hard_fallback"] = (df["generation_status"] == "length_fallback").astype(int)
    df["any_fallback"] = (df["fallback_count"] > 0).astype(int)
    return df


def compute_aggregate_metrics(df: pd.DataFrame, summary: dict) -> Dict[str, float]:
    """Compute the comparison metrics from a merged run DataFrame."""
    n = len(df)
    return {
        "n_mcqs": n,
        "cost_usd": summary.get("estimated_cost_usd", np.nan),
        "perfect_consensus_rate": df["perfect_consensus"].mean(),
        "hcw_rate": df["hcw"].mean(),
        "partial_plus_fallback_rate": df["partial_or_fallback"].mean(),
        "hard_fallback_rate": df["hard_fallback"].mean(),
        "consensus_accuracy": df["consensus_correct"].mean(),
        "mean_fallback_count": df["fallback_count"].mean(),
        "mean_length_replaced": df["length_replaced"].mean(),
        "mean_leak_replaced": df["leak_replaced"].mean(),
        "mean_nli_replaced": df["nli_replaced"].mean(),
        "duplicate_options_count": int(df["duplicate_options"].sum()) if "duplicate_options" in df.columns else 0,
    }


def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def per_language_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-language summary for each run."""
    rows = []
    for lang, g in df.groupby("language"):
        n = len(g)
        k = int(g["consensus_correct"].sum())
        lo, hi = wilson_ci(k, n)
        rows.append(
            {
                "language": lang,
                "n": n,
                "consensus_accuracy": k / n,
                "accuracy_ci_low": lo,
                "accuracy_ci_high": hi,
                "perfect_consensus_rate": g["perfect_consensus"].mean(),
                "hcw_rate": g["hcw"].mean(),
                "partial_plus_fallback_rate": g["partial_or_fallback"].mean(),
                "hard_fallback_rate": g["hard_fallback"].mean(),
                "mean_fallback_count": g["fallback_count"].mean(),
                "mean_nli_replaced": g["nli_replaced"].mean(),
                "mean_leak_replaced": g["leak_replaced"].mean(),
                "mean_length_replaced": g["length_replaced"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("language").reset_index(drop=True)


def per_variant_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-variant summary."""
    rows = []
    for variant, g in df.groupby("variant"):
        rows.append(
            {
                "variant": variant,
                "n": len(g),
                "consensus_accuracy": g["consensus_correct"].mean(),
                "perfect_consensus_rate": g["perfect_consensus"].mean(),
                "hcw_rate": g["hcw"].mean(),
                "partial_plus_fallback_rate": g["partial_or_fallback"].mean(),
                "mean_fallback_count": g["fallback_count"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("variant").reset_index(drop=True)


def per_generator_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-generator summary."""
    rows = []
    for gen, g in df.groupby("generator_model"):
        rows.append(
            {
                "generator_model": gen,
                "n": len(g),
                "consensus_accuracy": g["consensus_correct"].mean(),
                "perfect_consensus_rate": g["perfect_consensus"].mean(),
                "hcw_rate": g["hcw"].mean(),
                "partial_plus_fallback_rate": g["partial_or_fallback"].mean(),
                "mean_fallback_count": g["fallback_count"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("generator_model").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------


def mcnemar_test(
    paired: pd.DataFrame, col_v68: str, col_v69: str, correction: bool = True
) -> Dict[str, float]:
    """
    McNemar's test for a binary paired outcome.
    Returns a dict with statistic, pvalue, and discordant pair counts.
    """
    sub = paired[[col_v68, col_v69]].dropna()
    table = pd.crosstab(sub[col_v68], sub[col_v69])

    # Ensure the table is 2x2.
    for idx in [0, 1]:
        if idx not in table.index:
            table.loc[idx] = 0
    for col in [0, 1]:
        if col not in table.columns:
            table[col] = 0
    table = table.loc[[0, 1], [0, 1]]

    # No discordant pairs -> no evidence of change.
    if table.iloc[0, 1] + table.iloc[1, 0] == 0:
        stat, pval = 0.0, 1.0
    else:
        result = mcnemar(table.values, exact=False, correction=correction)
        stat, pval = float(result.statistic), float(result.pvalue)
    return {
        "v68_col": col_v68,
        "v69_col": col_v69,
        "n_pairs": len(sub),
        "v68_rate": sub[col_v68].mean(),
        "v69_rate": sub[col_v69].mean(),
        "both_0": int(table.iloc[0, 0]),
        "v68_0_v69_1": int(table.iloc[0, 1]),
        "v68_1_v69_0": int(table.iloc[1, 0]),
        "both_1": int(table.iloc[1, 1]),
        "statistic": stat,
        "pvalue": pval,
    }


def wilcoxon_test(
    paired: pd.DataFrame, col_v68: str, col_v69: str
) -> Dict[str, float]:
    """Wilcoxon signed-rank test for a paired continuous outcome."""
    sub = paired[[col_v68, col_v69]].dropna()
    x = pd.to_numeric(sub[col_v68], errors="coerce")
    y = pd.to_numeric(sub[col_v69], errors="coerce")
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    if len(x) < 5 or np.allclose(x, y):
        return {
            "v68_col": col_v68,
            "v69_col": col_v69,
            "n_pairs": len(x),
            "v68_mean": float(x.mean()),
            "v69_mean": float(y.mean()),
            "statistic": 0.0 if len(x) >= 5 else np.nan,
            "pvalue": 1.0 if len(x) >= 5 else np.nan,
        }
    result = wilcoxon(x, y, correction=True)
    return {
        "v68_col": col_v68,
        "v69_col": col_v69,
        "n_pairs": len(x),
        "v68_mean": float(x.mean()),
        "v69_mean": float(y.mean()),
        "statistic": float(result.statistic),
        "pvalue": float(result.pvalue),
    }


def bootstrap_paired_diff(
    paired: pd.DataFrame,
    col_v68: str,
    col_v69: str,
    n_boot: int = 10_000,
    seed: int = 20260615,
) -> Dict[str, float]:
    """
    Bootstrap the paired difference (v69 - v68) for a continuous or binary
    variable. Returns mean diff and 95% percentile CI.
    """
    rng = np.random.default_rng(seed)
    sub = paired[[col_v68, col_v69]].dropna()
    x = pd.to_numeric(sub[col_v68], errors="coerce").values
    y = pd.to_numeric(sub[col_v69], errors="coerce").values
    diffs = y - x
    n = len(diffs)
    if n == 0:
        return {
            "v68_col": col_v68,
            "v69_col": col_v69,
            "mean_diff": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
        }
    boot_diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_diffs.append(diffs[idx].mean())
    boot_diffs = np.sort(boot_diffs)
    return {
        "v68_col": col_v68,
        "v69_col": col_v69,
        "mean_diff": float(diffs.mean()),
        "ci_low": float(boot_diffs[int(0.025 * n_boot)]),
        "ci_high": float(boot_diffs[int(0.975 * n_boot)]),
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_metric_bars(
    metrics_v68: Dict[str, float],
    metrics_v69: Dict[str, float],
    out_path: Path,
) -> None:
    """Bar plot comparing aggregate rates and mean counts."""
    metrics = [
        ("Perfect consensus", "perfect_consensus_rate", "%"),
        ("HCW", "hcw_rate", "%"),
        ("Partial+fallback", "partial_plus_fallback_rate", "%"),
        ("Hard fallback", "hard_fallback_rate", "%"),
        ("Consensus accuracy", "consensus_accuracy", "%"),
        ("Mean fallback count", "mean_fallback_count", "count"),
        ("Mean NLI repl.", "mean_nli_replaced", "count"),
        ("Mean leak repl.", "mean_leak_replaced", "count"),
    ]

    labels = [m[0] for m in metrics]
    v68_vals = [metrics_v68[m[1]] * 100 if m[2] == "%" else metrics_v68[m[1]] for m in metrics]
    v69_vals = [metrics_v69[m[1]] * 100 if m[2] == "%" else metrics_v69[m[1]] for m in metrics]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width / 2, v68_vals, width, label="v68 (corpus fallback)", color="#d62728")
    ax.bar(x + width / 2, v69_vals, width, label="v69 (LLM fallback)", color="#2ca02c")

    ax.set_ylabel("Value")
    ax.set_title("v68 vs v69: Aggregate quality metrics (N=5, same seed)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Annotate values.
    for i, (v68, v69) in enumerate(zip(v68_vals, v69_vals)):
        ax.text(i - width / 2, v68, f"{v68:.1f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + width / 2, v69, f"{v69:.1f}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_paired_scatter(
    paired: pd.DataFrame, out_path: Path
) -> None:
    """
    Scatter of paired outcomes: x = v68, y = v69, with jitter for binary
    variables and a diagonal reference line.
    """
    cols = [
        ("consensus_frac", "Consensus fraction"),
        ("fallback_count", "Fallback count"),
        ("nli_replaced", "NLI replacements"),
        ("leak_replaced", "Leak replacements"),
    ]

    fig, axes = plt.subplots(1, len(cols), figsize=(16, 4.5))
    for ax, (col, title) in zip(axes, cols):
        x = pd.to_numeric(paired[f"{col}_v68"], errors="coerce")
        y = pd.to_numeric(paired[f"{col}_v69"], errors="coerce")
        valid = x.notna() & y.notna()
        x, y = x[valid], y[valid]

        # Small jitter for discrete/binary variables.
        if col in {"fallback_count", "nli_replaced", "leak_replaced"}:
            x = x + np.random.normal(0, 0.05, size=len(x))
            y = y + np.random.normal(0, 0.05, size=len(y))

        ax.scatter(x, y, alpha=0.4, s=30)
        lim_min = min(x.min(), y.min())
        lim_max = max(x.max(), y.max())
        ax.plot([lim_min, lim_max], [lim_min, lim_max], "k--", lw=1)
        ax.set_xlabel(f"v68 {title}")
        ax.set_ylabel(f"v69 {title}")
        ax.set_title(title)
        ax.grid(True, linestyle=":", alpha=0.4)

    fig.suptitle("Paired outcomes: v68 vs v69 (jittered for discrete variables)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_delta_by_language(
    per_lang: pd.DataFrame, out_path: Path
) -> None:
    """Bar plot of v69 - v68 deltas per language for key rates."""
    wide = per_lang.pivot(index="language", columns="version", values="hcw_rate")
    if "v68" not in wide.columns or "v69" not in wide.columns:
        logger.warning("Cannot plot delta by language: missing v68/v69 columns.")
        return

    metrics = ["hcw_rate", "partial_plus_fallback_rate", "consensus_accuracy", "mean_fallback_count"]
    titles = ["HCW rate", "Partial+fallback rate", "Consensus accuracy", "Mean fallback count"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()
    for ax, metric, title in zip(axes, metrics, titles):
        wide = per_lang.pivot(index="language", columns="version", values=metric)
        wide = wide.reindex(["English", "Arabic", "Yoruba"])
        delta = wide["v69"] - wide["v68"]
        colors = ["#2ca02c" if d < 0 else "#d62728" for d in delta]
        delta.plot(kind="bar", ax=ax, color=colors)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"v69 - v68: {title}")
        ax.set_ylabel("Delta")
        ax.set_xlabel("Language")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.suptitle("Per-language deltas: v69 (LLM fallback) vs v68 (corpus fallback)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Decision rule
# ---------------------------------------------------------------------------


def evaluate_gates(metrics_v69: Dict[str, float]) -> List[Dict[str, object]]:
    """Check v69 against absolute success gates."""
    results = []
    for metric, (op, target) in GATES.items():
        val = metrics_v69.get(metric, np.nan)
        if op == "<":
            passed = val < target
        elif op == "<=":
            passed = val <= target
        elif op == ">":
            passed = val > target
        elif op == ">=":
            passed = val >= target
        elif op == "==":
            passed = val == target
        else:
            passed = False
        results.append({"metric": metric, "value": val, "target": target, "op": op, "passed": passed})
    return results


def evaluate_relative_improvements(
    metrics_v68: Dict[str, float], metrics_v69: Dict[str, float]
) -> List[Dict[str, object]]:
    """Check v69 relative improvements over v68."""
    results = []
    for metric, (direction, threshold) in RELATIVE_IMPROVEMENTS.items():
        v68 = metrics_v68.get(metric, np.nan)
        v69 = metrics_v69.get(metric, np.nan)
        if v68 == 0:
            rel_change = np.inf if v69 != 0 else 0.0
        else:
            rel_change = (v69 - v68) / v68
        if direction == "decrease":
            passed = rel_change <= -threshold
        else:  # increase
            passed = rel_change >= threshold
        results.append(
            {
                "metric": metric,
                "v68": v68,
                "v69": v69,
                "rel_change": rel_change,
                "target_rel_change": -threshold if direction == "decrease" else threshold,
                "direction": direction,
                "passed": passed,
            }
        )
    return results


def classify_v69(
    gate_results: List[Dict[str, object]],
    rel_results: List[Dict[str, object]],
    cost_v69: float,
) -> Tuple[str, str]:
    """
    Classify v69 into STRONG PASS / MARGINAL / FAIL based on user thresholds.
    Returns (decision_label, explanation).
    """
    # Build quick lookup.
    gate = {r["metric"]: r for r in gate_results}
    rel = {r["metric"]: r for r in rel_results}

    hcw = gate.get("hcw_rate", {}).get("value", np.nan)
    pf = gate.get("partial_plus_fallback_rate", {}).get("value", np.nan)
    cost_ok = cost_v69 < COST_CAP_N5
    n15_cost_est = cost_v69 * 3 if not np.isnan(cost_v69) else np.nan

    # Strong pass: HCW <10%, partial+fallback <15%, cost <$1.50.
    strong_pass = (
        hcw < 0.10 and pf < 0.15 and cost_ok
    )

    # Fail: HCW >=15% or partial+fallback >=30% or cost >=$1.50.
    fail = (
        hcw >= 0.15 or pf >= 0.30 or not cost_ok
    )

    if strong_pass:
        decision = "STRONG PASS — SCALE to N=15 (v70)"
        explanation = (
            "v69 clears all primary gates (HCW <10%, partial+fallback <15%, cost <$1.50). "
            "Freeze the LLM-fallback config, run v70 at N=15, and sample 60 MCQs for human validation."
        )
    elif fail:
        decision = "FAIL — PIVOT to paper-first"
        explanation = (
            "v69 fails at least one primary gate (HCW >=15% or partial+fallback >=30% or cost >=$1.50). "
            "Do not scale to N=15. Treat v68/v69 as the experimental evidence, document the corpus-fallback "
            "bottleneck and LLM-fallback ablation, and move to human validation + paper drafting."
        )
    else:
        decision = "MARGINAL — CONDITIONAL SCALE or one more ablation"
        explanation = (
            "v69 is between strong pass and fail (HCW 10-15% or partial+fallback 15-30%). "
            "Scaling to N=15 (v70) is acceptable only with explicit caveats and a plan for one final "
            "quality-ablation if N=15 gates are not met; otherwise pivot to paper-first."
        )

    details = (
        f"HCW={hcw:.1%}, partial+fallback={pf:.1%}, cost=${cost_v69:.4f}, "
        f"estimated N=15 cost=${n15_cost_est:.4f}. "
    )
    return decision, details + explanation


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    args = parse_args()

    root = Path(__file__).resolve().parent
    v68_dir = args.v68_dir or root.parent / "v68" / "openrouter_pilot1_test_output"
    v69_dir = args.v69_dir or root / "openrouter_pilot1_test_output"
    out_dir = args.out_dir or root
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading v68 from %s", v68_dir)
    try:
        gen68, audit68, summary68 = load_run(v68_dir)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Cannot load v68: %s", exc)
        return 1
    gen68 = derive_binary_flags(merge_run_data(gen68, audit68))

    # v69 may not exist yet; if it doesn't, emit a template/placeholder report.
    if not v69_dir.exists():
        logger.warning("v69 data not found at %s. Writing v68-only baseline template.", v69_dir)
        metrics68 = compute_aggregate_metrics(gen68, summary68)
        per_lang68 = per_language_metrics(gen68)

        report_lines = [
            "# v68 vs v69 Comparison Report (TEMPLATE)",
            "",
            "v69 data not yet available. This is the v68-only baseline to be compared against v69.",
            "",
            "## v68 aggregate metrics (corpus-fallback baseline)",
            "",
            pd.DataFrame([metrics68]).T.to_markdown(),
            "",
            "## v68 per-language metrics",
            "",
            per_lang68.to_markdown(index=False),
            "",
            "Run `python compare_v68_v69.py` again after the v69 Kaggle output is copied to:",
            f"`{v69_dir}`",
        ]
        report_path = out_dir / "v68_v69_comparison_report.md"
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info("Report written to %s", report_path)
        return 0

    logger.info("Loading v69 from %s", v69_dir)
    try:
        gen69, audit69, summary69 = load_run(v69_dir)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Cannot load v69: %s", exc)
        return 1
    gen69 = derive_binary_flags(merge_run_data(gen69, audit69))

    # Aggregate metrics.
    metrics68 = compute_aggregate_metrics(gen68, summary68)
    metrics69 = compute_aggregate_metrics(gen69, summary69)

    # Comparison table.
    comp_rows = []
    for k in metrics68:
        comp_rows.append(
            {
                "metric": k,
                "v68": metrics68[k],
                "v69": metrics69[k],
                "diff": metrics69[k] - metrics68[k],
            }
        )
    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(out_dir / "v68_v69_comparison_table.csv", index=False)

    # Per-language table.
    per_lang68 = per_language_metrics(gen68)
    per_lang69 = per_language_metrics(gen69)
    per_lang68["version"] = "v68"
    per_lang69["version"] = "v69"
    per_lang = pd.concat([per_lang68, per_lang69], ignore_index=True)
    per_lang.to_csv(out_dir / "v68_v69_per_language.csv", index=False)

    # Per-variant and per-generator tables.
    per_variant68 = per_variant_metrics(gen68)
    per_variant69 = per_variant_metrics(gen69)
    per_variant68["version"] = "v68"
    per_variant69["version"] = "v69"
    per_variant = pd.concat([per_variant68, per_variant69], ignore_index=True)
    per_variant.to_csv(out_dir / "v68_v69_per_variant.csv", index=False)

    per_generator68 = per_generator_metrics(gen68)
    per_generator69 = per_generator_metrics(gen69)
    per_generator68["version"] = "v68"
    per_generator69["version"] = "v69"
    per_generator = pd.concat([per_generator68, per_generator69], ignore_index=True)
    per_generator.to_csv(out_dir / "v68_v69_per_generator.csv", index=False)

    # Pairing.
    paired = pd.merge(
        gen68,
        gen69,
        on="match_key",
        how="inner",
        suffixes=("_v68", "_v69"),
    )
    paired.to_csv(out_dir / "v68_v69_paired_metrics.csv", index=False)
    logger.info("Paired MCQs: %d / v68=%d / v69=%d", len(paired), len(gen68), len(gen69))

    if len(paired) == 0:
        logger.warning("No paired MCQs found. Statistical comparison is not possible.")

    # Paired statistical tests.
    test_rows = []
    if len(paired) > 0:
        binary_outcomes = [
            ("consensus_correct_v68", "consensus_correct_v69", "Consensus correct"),
            ("hcw_v68", "hcw_v69", "High-consensus-wrong"),
            ("perfect_consensus_v68", "perfect_consensus_v69", "Perfect consensus"),
            ("partial_or_fallback_v68", "partial_or_fallback_v69", "Partial or fallback"),
            ("hard_fallback_v68", "hard_fallback_v69", "Hard fallback"),
            ("any_fallback_v68", "any_fallback_v69", "Any fallback"),
        ]

        for c68, c69, label in binary_outcomes:
            res = mcnemar_test(paired, c68, c69, correction=True)
            res["outcome"] = label
            test_rows.append(res)

        continuous_outcomes = [
            ("consensus_frac_v68", "consensus_frac_v69", "Consensus fraction"),
            ("fallback_count_v68", "fallback_count_v69", "Fallback count"),
            ("nli_replaced_v68", "nli_replaced_v69", "NLI replacements"),
            ("leak_replaced_v68", "leak_replaced_v69", "Leak replacements"),
            ("length_replaced_v68", "length_replaced_v69", "Length replacements"),
        ]

        for c68, c69, label in continuous_outcomes:
            res = wilcoxon_test(paired, c68, c69)
            res["outcome"] = label
            test_rows.append(res)
            boot = bootstrap_paired_diff(paired, c68, c69)
            boot["outcome"] = label + " (bootstrapped diff)"
            boot["statistic"] = np.nan
            boot["pvalue"] = np.nan
            test_rows.append(boot)

    tests_df = pd.DataFrame(test_rows)
    tests_df.to_csv(out_dir / "v68_v69_statistical_tests.csv", index=False)

    # Plots.
    if not args.no_plots:
        try:
            plot_metric_bars(metrics68, metrics69, out_dir / "fig_v68_v69_metric_bars.png")
            if len(paired) > 0:
                plot_paired_scatter(paired, out_dir / "fig_v68_v69_paired_scatter.png")
                plot_delta_by_language(per_lang, out_dir / "fig_v68_v69_delta_by_language.png")
            logger.info("Figures written to %s", out_dir)
        except Exception as exc:
            logger.warning("Figure generation failed: %s", exc)

    # Decision evaluation.
    gate_results = evaluate_gates(metrics69)
    rel_results = evaluate_relative_improvements(metrics68, metrics69)
    decision_label, decision_explanation = classify_v69(
        gate_results, rel_results, metrics69["cost_usd"]
    )

    # Build markdown report.
    report_lines = [
        "# ProverbGap Pilot 1 TEST — v68 vs v69 Statistical Comparison",
        "",
        "**Comparison:** corpus-fallback baseline (v68) vs. LLM-fallback ablation (v69)",
        "**Design:** N=5 per language, same seed (20260615), same 15 proverbs, same generators/variants/auditors.",
        f"**Paired MCQs:** {len(paired)} (v68 n={len(gen68)}, v69 n={len(gen69)})",
        "",
        "## 1. Aggregate metrics",
        "",
        comp_df.to_markdown(index=False),
        "",
        "## 2. Absolute success gates (v69)",
        "",
    ]

    gate_df = pd.DataFrame(gate_results)
    report_lines.append(gate_df.to_markdown(index=False))
    report_lines.append("")

    report_lines.append("## 3. Relative improvements (v69 vs v68)")
    report_lines.append("")
    rel_df = pd.DataFrame(rel_results)
    report_lines.append(rel_df.to_markdown(index=False))
    report_lines.append("")

    report_lines.append("## 4. Per-language metrics")
    report_lines.append("")
    report_lines.append(per_lang.to_markdown(index=False))
    report_lines.append("")

    report_lines.append("## 5. Per-variant metrics")
    report_lines.append("")
    report_lines.append(per_variant.to_markdown(index=False))
    report_lines.append("")

    report_lines.append("## 6. Per-generator metrics")
    report_lines.append("")
    report_lines.append(per_generator.to_markdown(index=False))
    report_lines.append("")

    if len(paired) > 0:
        report_lines.append("## 7. Paired statistical tests")
        report_lines.append("")
        report_lines.append(
            "Binary outcomes use McNemar's test (corrected). "
            "Continuous outcomes use Wilcoxon signed-rank and a bootstrapped 95% CI for the paired difference."
        )
        report_lines.append("")
        display_cols = [
            "outcome",
            "n_pairs",
            "v68_rate",
            "v69_rate",
            "v68_mean",
            "v69_mean",
            "mean_diff",
            "ci_low",
            "ci_high",
            "statistic",
            "pvalue",
        ]
        display_tests = tests_df[[c for c in display_cols if c in tests_df.columns]].copy()
        report_lines.append(display_tests.to_markdown(index=False))
        report_lines.append("")
    else:
        report_lines.append("## 7. Paired statistical tests")
        report_lines.append("")
        report_lines.append("No paired MCQs available for statistical testing.")
        report_lines.append("")

    report_lines.append("## 8. Go / no-go decision")
    report_lines.append("")
    report_lines.append(f"**Decision:** {decision_label}")
    report_lines.append("")
    report_lines.append(decision_explanation)
    report_lines.append("")
    report_lines.append(
        "Thresholds used: STRONG PASS if HCW<10% AND partial+fallback<15% AND cost<$1.50; "
        "FAIL if HCW>=15% OR partial+fallback>=30% OR cost>=$1.50; otherwise MARGINAL."
    )
    report_lines.append("")

    report_lines.extend([
        "## 9. Outputs",
        "",
        f"- Comparison table: `{out_dir / 'v68_v69_comparison_table.csv'}`",
        f"- Per-language table: `{out_dir / 'v68_v69_per_language.csv'}`",
        f"- Per-variant table: `{out_dir / 'v68_v69_per_variant.csv'}`",
        f"- Per-generator table: `{out_dir / 'v68_v69_per_generator.csv'}`",
        f"- Paired data: `{out_dir / 'v68_v69_paired_metrics.csv'}`",
        f"- Statistical tests: `{out_dir / 'v68_v69_statistical_tests.csv'}`",
        f"- Metric bar figure: `{out_dir / 'fig_v68_v69_metric_bars.png'}`",
        f"- Paired scatter figure: `{out_dir / 'fig_v68_v69_paired_scatter.png'}`",
        f"- Per-language delta figure: `{out_dir / 'fig_v68_v69_delta_by_language.png'}`",
    ])

    report_path = out_dir / "v68_v69_comparison_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    logger.info("Report written to %s", report_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
