#!/usr/bin/env python3
"""
Generate publication-ready figures from Kaggle run data.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_DIR = Path('input')
OUTPUT_DIR = Path('figures')
OUTPUT_DIR.mkdir(exist_ok=True)

# Set style
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

def save(fig, name):
    fig.savefig(OUTPUT_DIR / name, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {name}")

# Load data
results = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
encoder = pd.read_csv(INPUT_DIR / 'encoder_results.csv')
mcqs_s1 = pd.read_csv(INPUT_DIR / 'mcqs_strategy1.csv')
mcqs_s2 = pd.read_csv(INPUT_DIR / 'mcqs_strategy2.csv')

# Separate successful API calls from failures
ok_results = results[(results['error'].isna()) | (results['error'] == '')]
s1_ok = ok_results[ok_results['strategy'] == 'S1']
s2_ok = ok_results[ok_results['strategy'] == 'S2']

print(f"Generating figures from {len(results)} API evaluations ({len(ok_results)} successful)")
print(f"Encoder evaluations: {len(encoder)}")

# ── Figure 1: Overall Accuracy Comparison ────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

categories = ['Random\nBaseline', 'Strategy 1\n(S1)', 'Strategy 2\n(pipeline)', 'S2 Strict\n(non-fallback)', 'S2 Fallback']
# Use successful evals only for S1; S2 has 0 successful API evals in this run
s1_acc = 100 * s1_ok['hit'].mean() if len(s1_ok) > 0 else 0
s2_pipe_acc = 100 * s2_ok['hit'].mean() if len(s2_ok) > 0 else 0
s2_nf = results[(results['strategy'] == 'S2') & (results['fallback'] == False)]
s2_fb = results[(results['strategy'] == 'S2') & (results['fallback'] == True)]
s2_strict_acc = 100 * s2_nf['hit'].mean() if len(s2_nf) > 0 else 0
s2_fb_acc = 100 * s2_fb['hit'].mean() if len(s2_fb) > 0 else 0

values = [25.0, s1_acc, s2_pipe_acc, s2_strict_acc, s2_fb_acc]
colors = ['#cccccc', '#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=0.5)
ax.axhline(y=25.0, color='red', linestyle='--', alpha=0.5, label='Random baseline (25%)')
ax.set_ylabel('Accuracy (%)')
ax.set_title('ProverbGap N=50 Pilot — Overall Accuracy (API Committee)', fontweight='bold')
ax.set_ylim(0, 105)

for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

ax.legend()
fig.tight_layout()
save(fig, 'fig1_overall_accuracy.png')

# ── Figure 2: Per-Model Accuracy (Successful Evaluations Only) ───────────────
fig, ax = plt.subplots(figsize=(9, 5))

models = sorted(s1_ok['model'].unique())
acc_values = [100 * s1_ok[s1_ok['model'] == m]['hit'].mean() for m in models]
n_values = [len(s1_ok[s1_ok['model'] == m]) for m in models]

# Clean model names for display
model_labels = [m.split('/')[-1][:25] for m in models]

bars = ax.barh(model_labels, acc_values, color=['#3498db', '#2ecc71', '#e67e22'], edgecolor='black')
ax.axvline(x=25.0, color='red', linestyle='--', alpha=0.5, label='Random baseline')
ax.set_xlabel('Accuracy (%)')
ax.set_title('Per-Model Accuracy — Strategy 1 (Successful API Evals Only)', fontweight='bold')
ax.set_xlim(0, 105)

for bar, val, n in zip(bars, acc_values, n_values):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}% (n={n})', va='center', fontsize=9)

ax.legend()
fig.tight_layout()
save(fig, 'fig2_per_model_accuracy.png')

# ── Figure 3: Encoder Baseline Comparison ────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

enc_models = sorted(encoder['model'].unique())
s1_enc = [100 * encoder[(encoder['model'] == m) & (encoder['strategy'] == 'S1')]['hit'].mean() for m in enc_models]
s2_enc = [100 * encoder[(encoder['model'] == m) & (encoder['strategy'] == 'S2')]['hit'].mean() for m in enc_models]

x = np.arange(len(enc_models))
width = 0.35

bars1 = ax.bar(x - width/2, s1_enc, width, label='Strategy 1', color='#3498db', edgecolor='black')
bars2 = ax.bar(x + width/2, s2_enc, width, label='Strategy 2', color='#9b59b6', edgecolor='black')

ax.axhline(y=25.0, color='red', linestyle='--', alpha=0.5, label='Random baseline')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Encoder Baseline Performance (Zero-Shot Cosine Similarity)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(enc_models)
ax.set_ylim(0, 105)
ax.legend()

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

fig.tight_layout()
save(fig, 'fig3_encoder_baselines.png')

# ── Figure 4: Per-Language Accuracy ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

langs = ['English', 'Arabic', 'Yoruba']
s1_lang = [100 * s1_ok[s1_ok['language'] == l]['hit'].mean() if len(s1_ok[s1_ok['language'] == l]) > 0 else 0 for l in langs]
enc_lang = [100 * encoder[encoder['language'] == l]['hit'].mean() for l in langs]

x = np.arange(len(langs))
width = 0.35

bars1 = ax.bar(x - width/2, s1_lang, width, label='S1 API (successful)', color='#2ecc71', edgecolor='black')
bars2 = ax.bar(x + width/2, enc_lang, width, label='Encoder (avg)', color='#e67e22', edgecolor='black')

ax.axhline(y=25.0, color='red', linestyle='--', alpha=0.5)
ax.set_ylabel('Accuracy (%)')
ax.set_title('Per-Language Accuracy Comparison', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(langs)
ax.set_ylim(0, 105)
ax.legend()

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

fig.tight_layout()
save(fig, 'fig4_per_language.png')

# ── Figure 5: S2 Generation Quality ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

s2_by_lang = mcqs_s2.groupby('language')['fallback'].agg(['sum', 'count'])
s2_by_lang['success'] = s2_by_lang['count'] - s2_by_lang['sum']
s2_by_lang['fallback_pct'] = 100 * s2_by_lang['sum'] / s2_by_lang['count']

langs = s2_by_lang.index.tolist()
success = s2_by_lang['success'].values
fallback = s2_by_lang['sum'].values

bars1 = ax.bar(langs, success, label='Generated (non-fallback)', color='#2ecc71', edgecolor='black')
bars2 = ax.bar(langs, fallback, bottom=success, label='Fallback', color='#e74c3c', edgecolor='black')

ax.set_ylabel('Number of MCQs')
ax.set_title('S2 Generation Quality — LLM Paraphrasing (qwen3-32b)', fontweight='bold')
ax.legend()

for i, (lang, row) in enumerate(s2_by_lang.iterrows()):
    ax.text(i, row['count'] + 1, f"{row['fallback_pct']:.0f}% fallback", ha='center', fontweight='bold')

fig.tight_layout()
save(fig, 'fig5_s2_generation_quality.png')

# ── Figure 6: Position Bias Check ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

pos_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
positions = ['A', 'B', 'C', 'D']

# Use S1 successful evals for position bias
mcq_map = {str(r['sample_id']): r for _, r in mcqs_s1.iterrows()}
hits_by_pos = {0: [], 1: [], 2: [], 3: []}
for _, row in s1_ok.iterrows():
    sid = str(row['sample_id'])
    if sid in mcq_map:
        pos = pos_map.get(str(mcq_map[sid]['Answer']), None)
        if pos is not None:
            hits_by_pos[pos].append(row['hit'])

accs = [100 * np.mean(hits_by_pos.get(p, [0])) for p in [0, 1, 2, 3]]
ns = [len(hits_by_pos.get(p, [])) for p in [0, 1, 2, 3]]

bars = ax.bar(positions, accs, color=['#3498db', '#9b59b6', '#e67e22', '#2ecc71'], edgecolor='black')
ax.axhline(y=25.0, color='red', linestyle='--', alpha=0.5, label='Random baseline')
ax.axhline(y=np.mean(accs), color='gray', linestyle=':', alpha=0.5, label=f'Mean = {np.mean(accs):.1f}%')
ax.set_ylabel('Accuracy (%)')
ax.set_xlabel('Correct Answer Position')
ax.set_title('Position Bias Check — S1 (Successful Evals Only)', fontweight='bold')
ax.set_ylim(0, 105)
ax.legend()

for bar, val, n in zip(bars, accs, ns):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val:.1f}%\n(n={n})', ha='center', va='bottom', fontsize=9)

fig.tight_layout()
save(fig, 'fig6_position_bias.png')

print(f"\nAll figures saved to {OUTPUT_DIR}/")
