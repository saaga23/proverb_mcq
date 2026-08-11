"""Per-auditor accuracy vs gold from v68 data.

For each auditor model in the audit committee,
compute accuracy against the curated gold meaning (correct_label).
Also compute pairwise Cohen's kappa between auditors.

Traceability: pilot1_test_generated_mcqs.csv + pilot1_test_audit_results.csv
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / "openrouter_pilot1_test_output"
OUT = BASE.parent

CATEGORIES = ["A", "B", "C", "D"]

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)

def cohen_kappa(a: list[str], b: list[str]) -> float:
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

    # Auditor columns
    auditors = [
        ("meta-llama_llama-3.3-70b-instruct", "vote_meta-llama_llama-3.3-70b-instruct"),
        ("mistralai_mistral-small-3.2-24b-instruct", "vote_mistralai_mistral-small-3.2-24b-instruct"),
        ("google_gemma-3-27b-it", "vote_google_gemma-3-27b-it"),
        ("deepseek_deepseek-v3.2", "vote_deepseek_deepseek-v3.2"),
    ]

    rows = [["auditor", "n_total", "n_correct_vs_gold", "accuracy_vs_gold", "ci_lower", "ci_upper"]]
    vote_vectors = {}
    for aud_name, vote_col in auditors:
        correct = 0
        total = 0
        vals_binary = []
        vals_letters = []
        for r in merged:
            gold = r.get("correct_label", "").strip().upper()
            vote = r.get(vote_col, "").strip().upper()
            if gold in CATEGORIES and vote in CATEGORIES:
                total += 1
                hit = 1 if vote == gold else 0
                correct += hit
                vals_binary.append(hit)
                vals_letters.append(vote)
        acc = correct / total if total else 0.0
        vote_vectors[aud_name] = vals_letters
        rows.append([aud_name, total, correct, round(acc, 4), "", ""])

    # Pairwise Cohen kappa on actual vote letters
    aud_names = [a[0] for a in auditors]
    kappa_rows = [["auditor_a", "auditor_b", "cohen_kappa"]]
    for i in range(len(aud_names)):
        for j in range(i + 1, len(aud_names)):
            kappa = cohen_kappa(vote_vectors[aud_names[i]], vote_vectors[aud_names[j]])
            kappa_rows.append([aud_names[i], aud_names[j], round(kappa, 4)])

    out_path = OUT / "table_auditor_vs_gold.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)
        f.write("\n")
        w.writerows(kappa_rows)

    print(f"Wrote {out_path}")
    print("=== Per-Auditor Accuracy vs Gold ===")
    for row in rows[1:]:
        print(row)
    print("\n=== Pairwise Cohen Kappa ===")
    for row in kappa_rows[1:]:
        print(row)

if __name__ == "__main__":
    main()
