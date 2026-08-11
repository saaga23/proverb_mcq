#!/usr/bin/env python3
"""
Analyze Kaggle Run Output — ProverbGap N=50
============================================
Comprehensive analysis of evaluation results, encoder baselines, MCQ quality,
position bias, statistical significance, and scale readiness.

Usage:
    python analyze_kaggle_run.py

Input:  kaggle_analysis/input/*.csv
Output: kaggle_analysis/analysis_output/*.csv
        kaggle_analysis/reports/scale_readiness_report.md
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

INPUT_DIR = Path('input')
OUTPUT_DIR = Path('analysis_output')
REPORT_DIR = Path('reports')
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

def load_or_exit(path, desc):
    if not path.exists():
        print(f"[ERROR] Missing {desc}: {path}")
        print("Place Kaggle output files in kaggle_analysis/input/")
        sys.exit(1)
    return pd.read_csv(path)

print("=" * 70)
print("  ProverbGap Kaggle Run Analysis")
print("=" * 70)

# ── Load Data ────────────────────────────────────────────────────────────────
try:
    results = load_or_exit(INPUT_DIR / 'evaluation_results.csv', 'API evaluation results')
    encoder = load_or_exit(INPUT_DIR / 'encoder_results.csv', 'Encoder baseline results')
    mcqs_s1 = load_or_exit(INPUT_DIR / 'mcqs_strategy1.csv', 'S1 MCQs')
    mcqs_s2 = load_or_exit(INPUT_DIR / 'mcqs_strategy2.csv', 'S2 MCQs')
except SystemExit:
    raise
except Exception as e:
    print(f"[FATAL] Failed to load data: {e}")
    sys.exit(1)

print(f"\n[LOADED]")
print(f"  API results:    {len(results)} rows")
print(f"  Encoder results:{len(encoder)} rows")
print(f"  S1 MCQs:        {len(mcqs_s1)} items")
print(f"  S2 MCQs:        {len(mcqs_s2)} items")

# ── Main Results Table ───────────────────────────────────────────────────────
print("\n[ANALYZING] Main results...")

s1_df = results[results['strategy'] == 'S1']
s2_df = results[results['strategy'] == 'S2']
s2_nf = s2_df[s2_df['fallback'] == False]
s2_fb = s2_df[s2_df['fallback'] == True]

main_table = []
main_table.append({
    'Metric': 'Random baseline',
    'Accuracy (%)': 25.0,
    'N': '-',
    'Notes': 'Theoretical 4-option uniform'
})
main_table.append({
    'Metric': 'Strategy 1 (S1)',
    'Accuracy (%)': round(100 * s1_df['hit'].mean(), 1),
    'N': len(s1_df),
    'Notes': 'Negative sampling distractors'
})
main_table.append({
    'Metric': 'Strategy 2 (pipeline)',
    'Accuracy (%)': round(100 * s2_df['hit'].mean(), 1),
    'N': len(s2_df),
    'Notes': 'All S2 items including fallbacks'
})
main_table.append({
    'Metric': 'Strategy 2 (strict)',
    'Accuracy (%)': round(100 * s2_nf['hit'].mean(), 1) if len(s2_nf) > 0 else 0,
    'N': len(s2_nf),
    'Notes': 'Non-fallback S2 items only'
})
main_table.append({
    'Metric': 'Strategy 2 (fallback)',
    'Accuracy (%)': round(100 * s2_fb['hit'].mean(), 1) if len(s2_fb) > 0 else 0,
    'N': len(s2_fb),
    'Notes': 'Fallback placeholder items'
})

pd.DataFrame(main_table).to_csv(OUTPUT_DIR / 'main_results_table.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'main_results_table.csv'}")

# ── Per-Model Breakdown ──────────────────────────────────────────────────────
print("\n[ANALYZING] Per-model breakdown...")
model_rows = []
for model in sorted(results['model'].unique()):
    m_s1 = s1_df[s1_df['model'] == model]
    m_s2 = s2_df[s2_df['model'] == model]
    m_s2_nf = s2_nf[s2_nf['model'] == model]
    
    # Failure rate
    failures_s1 = (m_s1['error'].notna() & (m_s1['error'] != '')).sum()
    failures_s2 = (m_s2['error'].notna() & (m_s2['error'] != '')).sum()
    
    model_rows.append({
        'Model': model,
        'S1_Acc': round(100 * m_s1['hit'].mean(), 1) if len(m_s1) > 0 else 0,
        'S2_Acc': round(100 * m_s2['hit'].mean(), 1) if len(m_s2) > 0 else 0,
        'S2_Strict_Acc': round(100 * m_s2_nf['hit'].mean(), 1) if len(m_s2_nf) > 0 else 0,
        'S1_Failures': int(failures_s1),
        'S2_Failures': int(failures_s2),
        'Total_Evals': len(m_s1) + len(m_s2),
    })

pd.DataFrame(model_rows).to_csv(OUTPUT_DIR / 'per_model_breakdown.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'per_model_breakdown.csv'}")

# ── Per-Language Breakdown ───────────────────────────────────────────────────
print("\n[ANALYZING] Per-language breakdown...")
lang_rows = []
for lang in ['English', 'Arabic', 'Yoruba']:
    l_s1 = s1_df[s1_df['language'] == lang]
    l_s2 = s2_df[s2_df['language'] == lang]
    l_s2_nf = s2_nf[s2_nf['language'] == lang]
    lang_rows.append({
        'Language': lang,
        'S1_Acc': round(100 * l_s1['hit'].mean(), 1) if len(l_s1) > 0 else 0,
        'S2_Acc': round(100 * l_s2['hit'].mean(), 1) if len(l_s2) > 0 else 0,
        'S2_Strict_Acc': round(100 * l_s2_nf['hit'].mean(), 1) if len(l_s2_nf) > 0 else 0,
        'N_S1': len(l_s1),
        'N_S2': len(l_s2),
    })

pd.DataFrame(lang_rows).to_csv(OUTPUT_DIR / 'per_language_breakdown.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'per_language_breakdown.csv'}")

# ── Position Bias Analysis ───────────────────────────────────────────────────
print("\n[ANALYZING] Position bias...")
pos_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
pos_rows = []

for strategy, df_strat, mcqs in [('S1', s1_df, mcqs_s1), ('S2', s2_df, mcqs_s2)]:
    mcq_map = {}
    for _, m in mcqs.iterrows():
        mcq_map[str(m['sample_id'])] = m
    
    hits_by_pos = {0: [], 1: [], 2: [], 3: []}
    for _, row in df_strat.iterrows():
        sid = str(row['sample_id'])
        if sid in mcq_map:
            pos = pos_map.get(str(mcq_map[sid]['Answer']), None)
            if pos is not None:
                hits_by_pos[pos].append(row['hit'])
    
    total_correct = sum(sum(h) for h in hits_by_pos.values())
    expected = total_correct / 4.0 if total_correct > 0 else 0
    
    for p in [0, 1, 2, 3]:
        hits = hits_by_pos.get(p, [])
        acc = 100 * np.mean(hits) if hits else 0
        label = ['A', 'B', 'C', 'D'][p]
        obs = sum(hits)
        chi2_contrib = ((obs - expected) ** 2 / expected) if expected > 0 else 0
        pos_rows.append({
            'Strategy': strategy,
            'Position': label,
            'Accuracy (%)': round(acc, 1),
            'N': len(hits),
            'Observed_Correct': int(obs),
            'Expected_Correct': round(expected, 1),
            'Chi2_Contribution': round(chi2_contrib, 2),
        })

pd.DataFrame(pos_rows).to_csv(OUTPUT_DIR / 'position_bias_report.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'position_bias_report.csv'}")

# ── Statistical Tests ────────────────────────────────────────────────────────
print("\n[ANALYZING] Statistical tests...")
stat_rows = []

# McNemar: S1 vs S2 (all)
merged = s1_df.merge(
    s2_df[['model', 'style', 'sample_id', 'hit']],
    on=['model', 'style', 'sample_id'],
    suffixes=('_s1', '_s2')
)
if len(merged) > 10:
    a = sum(1 for x, y in zip(merged['hit_s1'], merged['hit_s2']) if x == 1 and y == 1)
    b = sum(1 for x, y in zip(merged['hit_s1'], merged['hit_s2']) if x == 1 and y == 0)
    c = sum(1 for x, y in zip(merged['hit_s1'], merged['hit_s2']) if x == 0 and y == 1)
    d = sum(1 for x, y in zip(merged['hit_s1'], merged['hit_s2']) if x == 0 and y == 0)
    if b + c > 0:
        stat = (abs(b - c) - 1) ** 2 / (b + c)
        p = 1 - stats.chi2.cdf(stat, 1)
        stat_rows.append({
            'Test': 'McNemar (S1 vs S2, all)',
            'Statistic': round(stat, 3),
            'p_value': round(p, 4),
            'Significant (α=0.05)': 'YES' if p < 0.05 else 'NO',
            'N_pairs': len(merged),
            'Table': f"a={a},b={b},c={c},d={d}",
        })

# McNemar: S1 vs S2 (strict)
merged_nf = s1_df.merge(
    s2_nf[['model', 'style', 'sample_id', 'hit']],
    on=['model', 'style', 'sample_id'],
    suffixes=('_s1', '_s2'),
    how='inner'
)
if len(merged_nf) > 10:
    a = sum(1 for x, y in zip(merged_nf['hit_s1'], merged_nf['hit_s2']) if x == 1 and y == 1)
    b = sum(1 for x, y in zip(merged_nf['hit_s1'], merged_nf['hit_s2']) if x == 1 and y == 0)
    c = sum(1 for x, y in zip(merged_nf['hit_s1'], merged_nf['hit_s2']) if x == 0 and y == 1)
    d = sum(1 for x, y in zip(merged_nf['hit_s1'], merged_nf['hit_s2']) if x == 0 and y == 0)
    if b + c > 0:
        stat = (abs(b - c) - 1) ** 2 / (b + c)
        p = 1 - stats.chi2.cdf(stat, 1)
        stat_rows.append({
            'Test': 'McNemar (S1 vs S2, strict)',
            'Statistic': round(stat, 3),
            'p_value': round(p, 4),
            'Significant (α=0.05)': 'YES' if p < 0.05 else 'NO',
            'N_pairs': len(merged_nf),
            'Table': f"a={a},b={b},c={c},d={d}",
        })

pd.DataFrame(stat_rows).to_csv(OUTPUT_DIR / 'statistical_tests.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'statistical_tests.csv'}")

# ── Error Analysis ───────────────────────────────────────────────────────────
print("\n[ANALYZING] Error patterns...")
error_rows = []
for strategy in ['S1', 'S2']:
    df_strat = results[results['strategy'] == strategy]
    errors = df_strat[df_strat['error'].notna() & (df_strat['error'] != '')]
    error_rows.append({
        'Strategy': strategy,
        'Total_Evals': len(df_strat),
        'Error_Count': len(errors),
        'Error_Rate (%)': round(100 * len(errors) / len(df_strat), 2) if len(df_strat) > 0 else 0,
        'Top_Error': errors['error'].value_counts().index[0] if len(errors) > 0 else 'None',
    })

# Per-model error rates
for model in sorted(results['model'].unique()):
    m_df = results[results['model'] == model]
    errors = m_df[m_df['error'].notna() & (m_df['error'] != '')]
    error_rows.append({
        'Strategy': f'Model: {model}',
        'Total_Evals': len(m_df),
        'Error_Count': len(errors),
        'Error_Rate (%)': round(100 * len(errors) / len(m_df), 2) if len(m_df) > 0 else 0,
        'Top_Error': errors['error'].value_counts().index[0] if len(errors) > 0 else 'None',
    })

pd.DataFrame(error_rows).to_csv(OUTPUT_DIR / 'error_analysis.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'error_analysis.csv'}")

# ── Encoder Baseline Analysis ────────────────────────────────────────────────
print("\n[ANALYZING] Encoder baselines...")
enc_rows = []
for enc_name in sorted(encoder['model'].unique()):
    for strategy in ['S1', 'S2']:
        sub = encoder[(encoder['model'] == enc_name) & (encoder['strategy'] == strategy)]
        if len(sub) > 0:
            enc_rows.append({
                'Encoder': enc_name,
                'Strategy': strategy,
                'Accuracy (%)': round(100 * sub['hit'].mean(), 1),
                'N': len(sub),
            })

pd.DataFrame(enc_rows).to_csv(OUTPUT_DIR / 'encoder_baseline_results.csv', index=False)
print(f"  Saved: {OUTPUT_DIR / 'encoder_baseline_results.csv'}")

# ── S2 Fallback Rate ─────────────────────────────────────────────────────────
print("\n[ANALYZING] S2 generation quality...")
fb_rate = 100 * mcqs_s2['fallback'].sum() / len(mcqs_s2) if len(mcqs_s2) > 0 else 0
print(f"  S2 Fallback rate: {fb_rate:.1f}%")
print(f"  S2 Total items: {len(mcqs_s2)}")

# ── Scale Readiness Report ───────────────────────────────────────────────────
print("\n[WRITING] Scale readiness report...")

# Compute all checks
checks = {}
checks['fallback_rate_ok'] = fb_rate < 20
checks['api_failure_rate_ok'] = (error_rows[0]['Error_Rate (%)'] + error_rows[1]['Error_Rate (%)']) / 2 < 5 if len(error_rows) >= 2 else True
checks['encoder_works'] = len(encoder) > 0
checks['data_loaded'] = len(results) > 0
checks['mcqs_generated'] = len(mcqs_s1) > 0 and len(mcqs_s2) > 0

report_lines = []
report_lines.append("# Scale Readiness Report — ProverbGap N=50 → N=700")
report_lines.append("")
report_lines.append("## Executive Summary")
report_lines.append("")
all_pass = all(checks.values())
report_lines.append(f"**Overall: {'READY TO SCALE' if all_pass else 'BLOCKERS FOUND'}**")
report_lines.append("")

report_lines.append("## Individual Checks")
report_lines.append("")
report_lines.append(f"| Check | Status | Value | Threshold |")
report_lines.append(f"|-------|--------|-------|-----------|")
report_lines.append(f"| S2 Fallback Rate | {'PASS' if checks['fallback_rate_ok'] else 'FAIL'} | {fb_rate:.1f}% | < 20% |")
api_err_rate = (error_rows[0]['Error_Rate (%)'] + error_rows[1]['Error_Rate (%)']) / 2 if len(error_rows) >= 2 else 0
report_lines.append(f"| API Failure Rate | {'PASS' if checks['api_failure_rate_ok'] else 'FAIL'} | {api_err_rate:.1f}% | < 5% |")
report_lines.append(f"| Encoder Baselines | {'PASS' if checks['encoder_works'] else 'FAIL'} | {len(encoder)} rows | > 0 |")
report_lines.append(f"| Data Loaded | {'PASS' if checks['data_loaded'] else 'FAIL'} | {len(results)} rows | > 0 |")
report_lines.append(f"| MCQs Generated | {'PASS' if checks['mcqs_generated'] else 'FAIL'} | S1:{len(mcqs_s1)}, S2:{len(mcqs_s2)} | > 0 |")
report_lines.append("")

report_lines.append("## Key Metrics")
report_lines.append("")
report_lines.append(f"- **S1 Overall Accuracy**: {round(100 * s1_df['hit'].mean(), 1)}%")
report_lines.append(f"- **S2 Pipeline Accuracy**: {round(100 * s2_df['hit'].mean(), 1)}%")
report_lines.append(f"- **S2 Strict Accuracy**: {round(100 * s2_nf['hit'].mean(), 1) if len(s2_nf) > 0 else 0}%")
report_lines.append(f"- **Total API Evaluations**: {len(results)}")
report_lines.append(f"- **Total Encoder Evaluations**: {len(encoder)}")
report_lines.append("")

report_lines.append("## Per-Model API Performance")
report_lines.append("")
for row in model_rows:
    report_lines.append(f"- **{row['Model']}**: S1={row['S1_Acc']}%, S2={row['S2_Acc']}%, Failures={row['S1_Failures'] + row['S2_Failures']}")
report_lines.append("")

report_lines.append("## Recommendations for N=700 Scale")
report_lines.append("")
if not checks['fallback_rate_ok']:
    report_lines.append("- **CRITICAL**: S2 fallback rate is too high. Improve generation prompt or increase MAX_RETRIES before scaling.")
if not checks['api_failure_rate_ok']:
    report_lines.append("- **CRITICAL**: API failure rate is too high. Verify all keys are active and providers are healthy.")
if all_pass:
    report_lines.append("- All checks passed. The architecture is ready for scaling to N=700.")
    report_lines.append(f"- At N=700, expect {700 * 3 * 3 * 3 * 2} total evaluations (S1+S2 × 3 models × 3 styles × 3 languages × 2 strategies).")
    report_lines.append("- Estimated runtime: 6-12 hours depending on API rate limits.")
    report_lines.append("- Ensure Kaggle session timeout (9 hours) is sufficient, or run in batches.")

report_text = "\n".join(report_lines)
with open(REPORT_DIR / 'scale_readiness_report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"  Saved: {REPORT_DIR / 'scale_readiness_report.md'}")

print("\n" + "=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
print(f"\nOutput files in {OUTPUT_DIR}/:")
for f in sorted(OUTPUT_DIR.iterdir()):
    print(f"  - {f.name}")
print(f"\nReport: {REPORT_DIR / 'scale_readiness_report.md'}")
