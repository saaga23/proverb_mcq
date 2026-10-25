#!/usr/bin/env python3
"""`pytest` tests for v68 HCW threshold and length-fallback status calculations.

These tests verify that the canonical HCW definition (>= 0.75 consensus
fraction AND consensus != correct) produces the verified values from the
raw CSVs, and that the bootstrap CI script produces consistent results.
"""
import csv
import os
import sys
from collections import Counter
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V68_DIR = PROJECT_ROOT / "kaggle" / "run_logs" / "v68" / "openrouter_pilot1_test_output"
MCQS_CSV = V68_DIR / "pilot1_test_generated_mcqs.csv"
AUDIT_CSV = V68_DIR / "pilot1_test_audit_results.csv"

HCW_THRESHOLD = 0.75


def _load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [k.lstrip("\ufeff") for k in (reader.fieldnames or [])]
        return list(reader)


def _load_merged() -> list[dict]:
    mcqs = _load_csv(MCQS_CSV)
    audit = _load_csv(AUDIT_CSV)
    audit_by_mcq = {r["mcq_id"]: r for r in audit}
    merged = []
    for m in mcqs:
        a = audit_by_mcq.get(m["mcq_id"])
        if a:
            row = dict(m)
            row.update(a)
            merged.append(row)
    assert len(merged) == 180, f"Expected 180 merged rows, got {len(merged)}"
    return merged


@pytest.fixture(scope="module")
def merged_data():
    return _load_merged()


# --- Overall metrics ---

def test_total_mcqs(merged_data):
    assert len(merged_data) == 180

def test_consensus_accuracy(merged_data):
    correct = sum(1 for r in merged_data if r["consensus_correct"] == "1")
    assert correct == 102
    assert abs(correct / 180 - 0.5667) < 0.001

def test_perfect_consensus(merged_data):
    perfect = sum(1 for r in merged_data if float(r["consensus_frac"]) >= 0.9999)
    assert perfect == 75
    assert abs(perfect / 180 - 0.4167) < 0.001

def test_hcw_canonical_threshold(merged_data):
    """HCW = consensus_frac >= 0.75 AND consensus != correct."""
    hcw = sum(
        1 for r in merged_data
        if float(r["consensus_frac"]) >= HCW_THRESHOLD and r["consensus_correct"] == "0"
    )
    assert hcw == 50
    assert abs(hcw / 180 - 0.2778) < 0.001

def test_hcw_not_all_wrong_consensus(merged_data):
    """HCW (27.8%) must NOT equal all-wrong-consensus (43.3%)."""
    all_wrong = sum(1 for r in merged_data if r["consensus_correct"] == "0")
    assert all_wrong == 78  # 100% - 56.7% accuracy
    hcw = sum(
        1 for r in merged_data
        if float(r["consensus_frac"]) >= HCW_THRESHOLD and r["consensus_correct"] == "0"
    )
    assert hcw != all_wrong
    assert hcw < all_wrong

def test_length_fallback_status(merged_data):
    """Length fallback = generation_status == 'length_fallback' (not 'hard_fallback')."""
    lf = sum(1 for r in merged_data if r.get("generation_status", "") == "length_fallback")
    assert lf == 29
    assert abs(lf / 180 - 0.1611) < 0.001

def test_partial_plus_fallback(merged_data):
    pf = sum(
        1 for r in merged_data
        if r.get("generation_status", "") in ("partial", "length_fallback")
    )
    assert pf == 79
    assert abs(pf / 180 - 0.4389) < 0.001

def test_key_balance(merged_data):
    labels = Counter(r["correct_label"] for r in merged_data)
    assert labels["A"] == 45
    assert labels["B"] == 45
    assert labels["C"] == 45
    assert labels["D"] == 45


# --- Per-generator HCW ---

def test_per_generator_hcw(merged_data):
    expected = {
        "google/gemma-4-31b-it": (13, 21.7),
        "google/gemini-2.5-flash": (19, 31.7),
        "qwen/qwen3.7-max": (18, 30.0),
    }
    for gen, (count, rate) in expected.items():
        sub = [r for r in merged_data if r["generator_model"] == gen]
        hcw = sum(
            1 for r in sub
            if float(r["consensus_frac"]) >= HCW_THRESHOLD and r["consensus_correct"] == "0"
        )
        assert hcw == count, f"{gen}: expected {count}, got {hcw}"
        assert abs(hcw / len(sub) - rate / 100) < 0.001


# --- Per-variant HCW ---

def test_per_variant_hcw(merged_data):
    expected = {
        "adversarial-hard-negative": (11, 24.4),
        "adversarial-length-locked": (16, 35.6),
        "overgenerate-select": (10, 22.2),
        "taxonomy-guided": (13, 28.9),
    }
    for var, (count, rate) in expected.items():
        sub = [r for r in merged_data if r["variant"] == var]
        hcw = sum(
            1 for r in sub
            if float(r["consensus_frac"]) >= HCW_THRESHOLD and r["consensus_correct"] == "0"
        )
        assert hcw == count, f"{var}: expected {count}, got {hcw}"
        assert abs(hcw / len(sub) - rate / 100) < 0.001


# --- Per-language HCW ---

def test_per_language_hcw(merged_data):
    expected = {
        "English": (11, 18.3),
        "Arabic": (19, 31.7),
        "Yoruba": (20, 33.3),
    }
    for lang, (count, rate) in expected.items():
        sub = [r for r in merged_data if r["language"] == lang]
        hcw = sum(
            1 for r in sub
            if float(r["consensus_frac"]) >= HCW_THRESHOLD and r["consensus_correct"] == "0"
        )
        assert hcw == count, f"{lang}: expected {count}, got {hcw}"
        assert abs(hcw / len(sub) - rate / 100) < 0.001


# --- Position bias ---

def test_position_balance(merged_data):
    for pos in ["A", "B", "C", "D"]:
        sub = [r for r in merged_data if r["correct_label"] == pos]
        assert len(sub) == 45


# --- Bootstrap CI consistency ---

def test_bootstrap_ci_csv_consistency():
    """The bootstrap CI CSV must use the same HCW definition (>= 0.75)."""
    csv_path = PROJECT_ROOT / "kaggle" / "run_logs" / "v68" / "table_bootstrap_cis.csv"
    rows = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows[r["metric"]] = r
    assert abs(float(rows["hcw_rate"]["point_estimate"]) - 0.2778) < 0.001
    assert abs(float(rows["hard_fallback_rate"]["point_estimate"]) - 0.1611) < 0.001
    assert float(rows["hcw_rate"]["ci_lower_95"]) > 0.15
    assert float(rows["hcw_rate"]["ci_upper_95"]) < 0.40


def test_paper_bootstrap_csv_consistency():
    """The paper's bootstrap CSV must match the kaggle output values."""
    paper_csv = PROJECT_ROOT / "paper" / "tables" / "table_bootstrap_cis.csv"
    kaggle_csv = PROJECT_ROOT / "kaggle" / "run_logs" / "v68" / "table_bootstrap_cis.csv"
    paper_rows = {}
    kaggle_rows = {}
    for path, d in [(paper_csv, paper_rows), (kaggle_csv, kaggle_rows)]:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                d[r["metric"]] = r
    assert abs(
        float(paper_rows["hcw_rate"]["point_estimate"])
        - float(kaggle_rows["hcw_rate"]["point_estimate"])
    ) < 0.001
    assert abs(
        float(paper_rows["hard_fallback_rate"]["point_estimate"])
        - float(kaggle_rows["hard_fallback_rate"]["point_estimate"])
    ) < 0.001


def test_paper_pass_fail_labels():
    """The paper must mark hard fallback (16.1% vs <5% target) as a failure."""
    paper_path = PROJECT_ROOT / "paper" / "sections" / "05_results.md"
    content = paper_path.read_text(encoding="utf-8")
    hard_fallback_line = [l for l in content.split("\n") if "Hard fallback" in l and "16.1" in l]
    assert len(hard_fallback_line) == 1
    line = hard_fallback_line[0]
    assert ("FAIL" in line or "\u274c" in line), f"Expected FAIL or X emoji, got: {line}"
    assert "PASS" not in line and "OK" not in line, f"Should not be PASS/OK: {line}"
