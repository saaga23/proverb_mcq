"""Generate figures for ProverbGap paper."""
from __future__ import annotations

import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "kaggle" / "run_logs" / "v68"
OUT = Path(__file__).resolve().parent.parent / "paper" / "figures"

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def save_fig(name: str):
    path = OUT / name
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# Figure 2: Per-language consensus accuracy with Wilson CIs
def fig2():
    data = [
        ("English", 0.65, 0.524, 0.758),
        ("Arabic", 0.533, 0.409, 0.654),
        ("Yoruba", 0.517, 0.393, 0.638),
    ]
    langs, accs, los, his = zip(*data)
    x = np.arange(len(langs))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(x, accs, color=["#4C78A8", "#F58518", "#E45756"], edgecolor="black")
    ax.errorbar(x, accs, yerr=[[a - l for a, l in zip(accs, los)], [h - a for a, h in zip(accs, his)]], fmt="none", color="black", capsize=5)
    ax.axhline(0.25, color="gray", linestyle="--", label="Random (25%)")
    ax.set_xticks(x)
    ax.set_xticklabels(langs)
    ax.set_ylabel("Consensus Accuracy")
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.set_title("Per-Language Consensus Accuracy (v68 N=5)")
    save_fig("fig2_per_language_accuracy.png")

# Figure 3: Position bias
def fig3():
    positions = ["A", "B", "C", "D"]
    accs = [0.733, 0.578, 0.489, 0.467]
    colors = ["#4C78A8" if a > 0.6 else "#F58518" if a > 0.5 else "#E45756" for a in accs]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(positions, accs, color=colors, edgecolor="black")
    ax.axhline(0.5667, color="gray", linestyle="--", label="Overall (56.7%)")
    ax.set_ylabel("Consensus Accuracy")
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.set_title("Position Bias: Accuracy by Correct-Key Position")
    save_fig("fig3_position_bias.png")

# Figure 4: Fallback count heatmap (variant x language)
def fig4():
    data = load_csv(BASE / "table_variant_language_interaction.csv")
    variants = sorted(set(r["variant"] for r in data))
    languages = ["English", "Arabic", "Yoruba"]
    matrix = np.zeros((len(variants), len(languages)))
    for r in data:
        vi = variants.index(r["variant"])
        li = languages.index(r["language"])
        matrix[vi, li] = float(r["fallback_mean"])
    
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(np.arange(len(languages)))
    ax.set_yticks(np.arange(len(variants)))
    ax.set_xticklabels(languages)
    ax.set_yticklabels(variants)
    ax.set_title("Mean Fallback Count by Variant × Language")
    for i in range(len(variants)):
        for j in range(len(languages)):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, label="Fallback Count")
    save_fig("fig4_fallback_heatmap.png")

# Figure 5: Filter replacement breakdown
def fig5():
    data = load_csv(BASE / "table_filter_replacement_analysis.csv")
    overall = data[:6]  # first 6 rows are overall
    labels = [r["metric"] for r in overall]
    pcts = [float(r["pct_of_total_replacements"].replace("%", "")) for r in overall]
    colors = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(labels[::-1], pcts[::-1], color=colors[::-1], edgecolor="black")
    ax.set_xlabel("Percentage of Total Replacements")
    ax.set_title("Filter Replacement Breakdown (v68)")
    for i, v in enumerate(pcts[::-1]):
        ax.text(v + 1, i, f"{v:.1f}%", va="center")
    save_fig("fig5_filter_breakdown.png")

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig2()
    fig3()
    fig4()
    fig5()
    print("All figures generated.")
