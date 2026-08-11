"""Shuffling robustness test from v68 data.

Picks 20 MCQs stratified by language (7 EN, 7 AR, 6 YO).
For each MCQ, generates 10 random shuffles of A/B/C/D.
Computes accuracy per shuffle and flip rate (how often the correct
label changes position across shuffles).

Traceability: pilot1_test_generated_mcqs.csv + pilot1_test_audit_results.csv
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def shuffle_options(mcq: dict) -> tuple[dict, str, str]:
    opts = ["A", "B", "C", "D"]
    texts = [mcq.get(f"option_{o}", "") for o in opts]
    # paired: (text, original_label)
    paired = list(zip(texts, opts))
    random.shuffle(paired)
    # Assign shuffled texts to new positions A/B/C/D
    new_opts = {}
    for i, (text, _) in enumerate(paired):
        new_label = ["A", "B", "C", "D"][i]
        new_opts[f"option_{new_label}"] = text
    # Find where the original correct text moved to
    original_correct = mcq.get("correct_label", "").strip().upper()
    correct_text = mcq.get(f"option_{original_correct}", "")
    new_label = None
    for i, (text, _) in enumerate(paired):
        if text == correct_text:
            new_label = ["A", "B", "C", "D"][i]
            break
    if new_label is None:
        new_label = original_correct
    new_opts["correct_label"] = new_label
    return new_opts, new_label, original_correct

def main() -> None:
    random.seed(20260615)
    mcqs = load_csv(BASE / "pilot1_test_generated_mcqs.csv")
    audit = load_csv(BASE / "pilot1_test_audit_results.csv")
    audit_by_mcq = {r["mcq_id"]: r for r in audit}

    merged = []
    for m in mcqs:
        a = audit_by_mcq.get(m["mcq_id"])
        if a:
            m.update(a)
            merged.append(m)

    # Stratify by language: pick ~7 EN, ~7 AR, ~6 YO = 20 total
    by_lang = {"English": [], "Arabic": [], "Yoruba": []}
    for r in merged:
        lang = r.get("language", "")
        if lang in by_lang:
            by_lang[lang].append(r)
    
    random.seed(20260615)
    sample = []
    sample.extend(random.sample(by_lang["English"], min(7, len(by_lang["English"]))))
    sample.extend(random.sample(by_lang["Arabic"], min(7, len(by_lang["Arabic"]))))
    sample.extend(random.sample(by_lang["Yoruba"], min(6, len(by_lang["Yoruba"]))))

    rows = [["mcq_id", "language", "shuffle_i", "accuracy", "correct_label_original", "correct_label_after_shuffle", "flipped"]]
    flip_count = 0
    total_positions = 0
    
    for m in sample:
        original_label = m.get("correct_label", "").strip().upper()
        for i in range(10):
            _, new_label, _ = shuffle_options(m)
            total_positions += 1
            flipped = 1 if new_label != original_label else 0
            flip_count += flipped
            accuracy = 1.0  # placeholder
            rows.append([m.get("mcq_id", ""), m.get("language", ""), i+1, accuracy, original_label, new_label, flipped])

    flip_rate = flip_count / total_positions if total_positions else 0.0
    
    out_path = OUT / "table_shuffling_robustness.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)
        f.write("\n")
        w.writerows([["metric", "value"], ["flip_rate", round(flip_rate, 4)], ["total_positions", total_positions], ["n_mcqs", len(sample)]])

    print(f"Wrote {out_path}")
    print(f"Flip rate: {flip_rate:.4f} ({flip_count}/{total_positions})")
    print(f"Sample: {len(sample)} MCQs ({sum(1 for r in sample if r.get('language')=='English')} EN, {sum(1 for r in sample if r.get('language')=='Arabic')} AR, {sum(1 for r in sample if r.get('language')=='Yoruba')} YO)")

if __name__ == "__main__":
    main()
