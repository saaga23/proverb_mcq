"""Inter-annotator agreement (IAA) for ProverbGap LLM-based annotators.

Computes, against the v68 blind-committee answer (`consensus_label`) and against
the gold curated meaning (`correct_label`):

  * per-model accuracy + refusal rate
  * per-language accuracy
  * pairwise Cohen's kappa between models
  * Fleiss' kappa across all LLM raters (each model = one rater)

Pure stdlib + pandas. No external ML deps.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

HERE = Path(__file__).resolve().parent
SAMPLE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "production"
    / "paper_first_outputs_2026-06-22_10-42-02"
    / "human_validation_sample_60.csv"
)
OUTPUT_DIR = HERE / "outputs"
CATEGORIES = ["A", "B", "C", "D"]


def _cohen_kappa(a: List[str], b: List[str]) -> float:
    pairs = [(x, y) for x, y in zip(a, b) if x in CATEGORIES and y in CATEGORIES]
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    cnt_a = {c: 0 for c in CATEGORIES}
    cnt_b = {c: 0 for c in CATEGORIES}
    for x, y in pairs:
        cnt_a[x] += 1
        cnt_b[y] += 1
    pe = sum((cnt_a[c] / n) * (cnt_b[c] / n) for c in CATEGORIES)
    if 1 - pe == 0:
        return 1.0 if po == 1.0 else float("nan")
    return (po - pe) / (1 - pe)


def _fleiss_kappa(table: Dict[str, List[str]]) -> float:
    """table: {rater: [answers per item]}. All raters aligned by index."""
    raters = list(table.keys())
    if not raters:
        return float("nan")
    n_items = min(len(table[r]) for r in raters)
    if n_items == 0:
        return float("nan")
    m = len(raters)
    # observed agreement per item
    p_bar_num = 0.0
    for i in range(n_items):
        counts = {c: 0 for c in CATEGORIES}
        valid = 0
        for r in raters:
            v = table[r][i]
            if v in CATEGORIES:
                counts[v] += 1
                valid += 1
        if valid == 0:
            continue
        # proportion of agreements for this item
        agree = sum(c * (c - 1) for c in counts.values())
        p_bar_num += agree / (valid * (valid - 1)) if valid > 1 else 0.0
    p_bar = p_bar_num / n_items if n_items else float("nan")
    # chance agreement
    cat_tot = {c: 0 for c in CATEGORIES}
    total = 0
    for i in range(n_items):
        for r in raters:
            v = table[r][i]
            if v in CATEGORIES:
                cat_tot[v] += 1
                total += 1
    if total == 0:
        return float("nan")
    pe = sum((cat_tot[c] / total) ** 2 for c in CATEGORIES)
    if 1 - pe == 0:
        return 1.0 if p_bar == 1.0 else float("nan")
    return (p_bar - pe) / (1 - pe)


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    need = {"validation_id", "language", "consensus_label", "correct_label"}
    assert need.issubset(sample.columns), f"sample missing cols: {need - set(sample.columns)}"

    results: List[pd.DataFrame] = []
    for pat in ["openrouter_annotation_results_*.csv", "modal_annotation_results_*.csv"]:
        for f in sorted(OUTPUT_DIR.glob(pat)):
            df = pd.read_csv(f)
            if {"validation_id", "model", "answer"}.issubset(df.columns):
                results.append(df)
    if not results:
        raise SystemExit("No annotator result CSVs found in annotation/outputs/")
    ann = pd.concat(results, ignore_index=True)

    # Pivot: rows=validation_id, cols=model, values=answer
    pivot = ann.pivot_table(index="validation_id", columns="model", values="answer", aggfunc="first")

    report: Dict[str, object] = {"n_items": int(sample["validation_id"].nunique()), "models": list(pivot.columns)}
    summary_rows = []

    for model in pivot.columns:
        col = pivot[model]
        merged = sample.set_index("validation_id")[["consensus_label", "correct_label", "language"]]
        joined = col.to_frame("answer").join(merged)
        answered = joined[joined["answer"].isin(CATEGORIES)]
        n_total = len(joined)
        n_answered = len(answered)
        n_refusal = n_total - n_answered
        acc_consensus = (answered["answer"] == answered["consensus_label"]).mean() if n_answered else float("nan")
        acc_correct = (answered["answer"] == answered["correct_label"]).mean() if n_answered else float("nan")
        # per-language accuracy vs consensus
        per_lang = {}
        for lang in ["English", "Arabic", "Yoruba"]:
            sub = answered[answered["language"] == lang]
            per_lang[lang] = round((sub["answer"] == sub["consensus_label"]).mean(), 4) if len(sub) else None
        summary_rows.append({
            "model": model, "n_total": n_total, "n_answered": n_answered,
            "n_refusal": n_refusal, "acc_vs_consensus": round(float(acc_consensus), 4) if n_answered else None,
            "acc_vs_correct": round(float(acc_correct), 4) if n_answered else None,
            "per_lang": per_lang,
        })
    report["per_model"] = summary_rows

    # Pairwise Cohen's kappa (vs consensus ground truth alignment is per-model;
    # here we measure raw inter-model agreement on the answer letter)
    models = list(pivot.columns)
    pairwise = {}
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            m1, m2 = models[i], models[j]
            a = pivot[m1].where(pivot[m1].isin(CATEGORIES)).tolist()
            b = pivot[m2].where(pivot[m2].isin(CATEGORIES)).tolist()
            pairwise[f"{m1}__{m2}"] = round(_cohen_kappa(a, b), 4)
    report["pairwise_cohen_kappa"] = pairwise

    # Fleiss' kappa across all models (each model = rater)
    fleiss_table = {m: pivot[m].where(pivot[m].isin(CATEGORIES)).tolist() for m in models}
    report["fleiss_kappa_all_models"] = round(_fleiss_kappa(fleiss_table), 4)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_json = OUTPUT_DIR / f"iaa_report_{ts}.json"
    out_csv = OUTPUT_DIR / f"iaa_summary_{ts}.csv"
    out_json.write_text(json.dumps(report, indent=2, default=str))
    pd.DataFrame(summary_rows).to_csv(out_csv, index=False)

    print("=" * 70)
    print("IAA REPORT")
    print("=" * 70)
    print(f"Items: {report['n_items']} | Models: {len(models)}")
    print(f"Fleiss' kappa (all models as raters): {report['fleiss_kappa_all_models']}")
    print("-" * 70)
    for r in summary_rows:
        print(f"{r['model']:42s} ans={r['n_answered']:2d}/{r['n_total']:2d} "
              f"ref={r['n_refusal']:2d} acc_cons={r['acc_vs_consensus']} acc_gold={r['acc_vs_correct']}")
    print("-" * 70)
    print("Pairwise Cohen's kappa:")
    for k, v in pairwise.items():
        print(f"  {k}: {v}")
    print(f"\nWrote: {out_json.name}, {out_csv.name}")


if __name__ == "__main__":
    main()
