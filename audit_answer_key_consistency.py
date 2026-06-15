"""
Standalone audit script for ProverbGap Kaggle runs.

Checks whether eval_results.csv answer keys match the saved MCQ files.
Usage:
    python audit_answer_key_consistency.py <run_dir>

Example:
    python audit_answer_key_consistency.py kaggle_analysis/Last_run/extracted_new
"""

import sys
from pathlib import Path
import pandas as pd


def audit(run_dir: Path) -> dict:
    eval_path = run_dir / "eval_results.csv"
    mcq_path = run_dir / "mcqs_all.csv"

    if not eval_path.exists():
        raise FileNotFoundError(f"Missing {eval_path}")
    if not mcq_path.exists():
        raise FileNotFoundError(f"Missing {mcq_path}")

    eval_df = pd.read_csv(eval_path, encoding="utf-8-sig")
    mcq_df = pd.read_csv(mcq_path, encoding="utf-8-sig")

    # Strategy is encoded differently in eval vs mcq? Align.
    eval_df["strategy"] = eval_df["strategy"].astype(str).str.strip()
    mcq_df["strategy"] = mcq_df["strategy"].astype(str).str.strip()

    mcq_keys = mcq_df[["sample_id", "strategy", "Answer"]].rename(columns={"Answer": "Answer_mcq"})
    merged = eval_df.merge(
        mcq_keys,
        on=["sample_id", "strategy"],
        how="left",
    )

    s1_merged = merged[merged["strategy"] == "S1"]
    s2_merged = merged[merged["strategy"] == "S2"]

    s1_mismatch = (s1_merged["correct"] != s1_merged["Answer_mcq"]).sum()
    s2_mismatch = (s2_merged["correct"] != s2_merged["Answer_mcq"]).sum()

    # Recompute accuracy using saved MCQ keys
    s1_valid = s1_merged[s1_merged["predicted"].notna()].copy()
    s1_valid["match_mcq"] = s1_valid["predicted"] == s1_valid["Answer_mcq"]
    s1_actual_acc = s1_valid["match_mcq"].mean() if len(s1_valid) > 0 else None

    s2_valid = s2_merged[s2_merged["predicted"].notna()].copy()
    s2_valid["match_mcq"] = s2_valid["predicted"] == s2_valid["Answer_mcq"]
    s2_actual_acc = s2_valid["match_mcq"].mean() if len(s2_valid) > 0 else None

    return {
        "eval_rows": len(eval_df),
        "s1_rows": len(s1_merged),
        "s1_mismatches": int(s1_mismatch),
        "s1_mismatch_pct": s1_mismatch / len(s1_merged) * 100 if len(s1_merged) > 0 else 0,
        "s2_rows": len(s2_merged),
        "s2_mismatches": int(s2_mismatch),
        "s2_mismatch_pct": s2_mismatch / len(s2_merged) * 100 if len(s2_merged) > 0 else 0,
        "s1_actual_accuracy": s1_actual_acc,
        "s2_actual_accuracy": s2_actual_acc,
    }


def main():
    if len(sys.argv) < 2:
        run_dir = Path("kaggle_analysis/Last_run/extracted_new")
    else:
        run_dir = Path(sys.argv[1])

    run_dir = run_dir.resolve()
    print(f"Auditing: {run_dir}")
    result = audit(run_dir)

    print(f"\nEval rows: {result['eval_rows']}")
    print(f"S1 rows: {result['s1_rows']} | mismatches: {result['s1_mismatches']} ({result['s1_mismatch_pct']:.1f}%)")
    print(f"S2 rows: {result['s2_rows']} | mismatches: {result['s2_mismatches']} ({result['s2_mismatch_pct']:.1f}%)")

    if result["s1_actual_accuracy"] is not None:
        print(f"\nS1 accuracy vs saved MCQ keys: {result['s1_actual_accuracy']:.3f}")
    if result["s2_actual_accuracy"] is not None:
        print(f"S2 accuracy vs saved MCQ keys: {result['s2_actual_accuracy']:.3f}")

    if result["s1_mismatches"] > 0 or result["s2_mismatches"] > 0:
        print("\nCRITICAL: answer-key mismatch detected. Do not trust printed accuracy numbers.")
        sys.exit(1)
    else:
        print("\nPASS: Answer keys are consistent. Accuracy numbers are valid for saved MCQs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
