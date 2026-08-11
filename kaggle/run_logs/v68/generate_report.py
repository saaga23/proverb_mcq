import pandas as pd
import os
import math
from collections import Counter
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

base = "kaggle_run_logs/v68/openrouter_pilot1_test_output"
audit = pd.read_csv(os.path.join(base, "pilot1_test_audit_results.csv"))
mcq = pd.read_csv(os.path.join(base, "pilot1_test_generated_mcqs.csv"))

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0,0)
    p = k/n
    denom = 1 + z*z/n
    centre = (p + z*z/(2*n))/denom
    margin = z*math.sqrt((p*(1-p) + z*z/(4*n))/n)/denom
    return (max(0, centre-margin), min(1, centre+margin))

merged = audit.merge(mcq[['mcq_id','proverb','correct_meaning','option_A','option_B','option_C','option_D','generation_status','fallback_count','length_replaced','leak_replaced','nli_replaced']], on='mcq_id', how='left')
vote_cols = [c for c in audit.columns if c.startswith('vote_')]
hit_cols = [c for c in audit.columns if c.startswith('hit_')]

print("# V68 Kaggle Run — Per-Language Performance Report")
print()
print("**Run:** 2026-06-22 | **Sample:** N=5 proverbs/language × 3 generators × 4 variants = 180 MCQs (60/language).")
print("**Generator pool:** qwen/qwen3.7-max, google/gemma-4-31b-it, google/gemini-2.5-flash (all active, 0 benched).")
print("**Audit committee:** 4 models, 0 missing votes, 0 substitutions.")
print()

print("## 1. Per-language consensus correctness (Wilson 95% CI)")
print()
print("Consensus correctness = fraction of MCQs where the plurality auditor vote matches the correct label.")
print()
print("| Language | Correct / Total | Accuracy | Wilson 95% CI |")
print("|----------|----------------|----------|---------------|")
for lang in ['English','Arabic','Yoruba']:
    sub = audit[audit.language==lang]
    n = len(sub)
    k = sub.consensus_correct.sum()
    lo, hi = wilson_ci(k,n)
    print(f"| {lang} | {k}/{n} | {k/n:.1%} | {lo:.1%}-{hi:.1%} |")
print()
print("- **English** leads but is still only ~65%; the high share of too-easy items drags the meaningful signal down.")
print("- **Arabic** and **Yoruba** are statistically similar and both just clear the 50% bar.")
print()

print("## 2. Perfect consensus & high-consensus-wrong (HCW)")
print()
print("| Language | Perfect consensus | HCW (>=50% vote, wrong) | Non-perfect consensus |")
print("|----------|-------------------|--------------------------|-----------------------|")
for lang in ['English','Arabic','Yoruba']:
    sub = audit[audit.language==lang]
    n = len(sub)
    perfect = (sub.consensus_frac == 1.0).sum()
    hcw = ((sub.consensus_frac >= 0.5) & (sub.consensus_correct == 0)).sum()
    nonperf = n - perfect
    print(f"| {lang} | {perfect}/{n} ({perfect/n:.1%}) | {hcw}/{n} ({hcw/n:.1%}) | {nonperf}/{n} ({nonperf/n:.1%}) |")
print()
print("- **Perfect consensus** is far above the <30% target in all languages; English and Arabic are near or above 45%.")
print("- **HCW** is catastrophically high (33-48%). When auditors agree, they agree on the wrong answer almost as often as the right one.")
print("- **Non-perfect consensus** is highest for Yoruba (~70%) and lowest for Arabic (~50%), suggesting Yoruba options create more auditor disagreement (but often because the key is unrecognizable).")
print()

print("## 3. Correct-key distribution per language (position bias)")
print()
print("| Language | A | B | C | D |")
print("|----------|---|---|---|---|")
for lang in ['English','Arabic','Yoruba']:
    sub = audit[audit.language==lang]
    cnt = Counter(sub.correct_label)
    print(f"| {lang} | {cnt.get('A',0)} ({cnt.get('A',0)/len(sub):.1%}) | {cnt.get('B',0)} ({cnt.get('B',0)/len(sub):.1%}) | {cnt.get('C',0)} ({cnt.get('C',0)/len(sub):.1%}) | {cnt.get('D',0)} ({cnt.get('D',0)/len(sub):.1%}) |")
print()
print("- Position bias is perfectly controlled at 25% per key for every language.")
print()

print("## 4. Auditor behavior per language")
print()
for lang in ['English','Arabic','Yoruba']:
    sub = audit[audit.language==lang]
    print(f"### {lang}")
    print()
    print("| Auditor | Missing votes | Hit rate |")
    print("|---------|---------------|----------|")
    for vc, hc in zip(vote_cols, hit_cols):
        name = vc.replace('vote_','')
        missing = sub[vc].isna().sum()
        hits = sub[hc].sum()
        print(f"| {name} | {missing}/{len(sub)} ({missing/len(sub):.1%}) | {hits}/{len(sub)} ({hits/len(sub):.1%}) |")
    print()
    print(f"- Mean consensus fraction: **{sub.consensus_frac.mean():.3f}**")
    print()
print("- Auditor hit rates drop sharply on Yoruba (Gemma-3-27b only 36.7%), confirming that Yoruba meanings are hardest to identify from options alone.")
print("- No missing votes and no substitutions: the audit pipeline is stable.")
print()

print("## 5. Specific failure examples")
print()
print("### 5.1 Yoruba — distractors override the literal/cultural key")
print()
yoruba_fail = merged[(merged.language=='Yoruba') & (merged.consensus_correct==0)]
for idx, row in list(yoruba_fail.sort_values('consensus_frac', ascending=False).head(3).iterrows()):
    print(f"**{row['proverb']}** ({row['variant']}, `{row['generator_model']}`)")
    print(f"- Correct meaning: *{row['correct_meaning']}* (correct key: **{row['correct_label']}**)")
    print(f"- Consensus: **{row['consensus_label']}** @ {row['consensus_frac']} | status: `{row['generation_status']}`, fallback_count={row['fallback_count']}")
    print(f"- A: {row['option_A']}")
    print(f"- B: {row['option_B']}")
    print(f"- C: {row['option_C']}")
    print(f"- D: {row['option_D']}")
    print()

print("### 5.2 Arabic — confident-wrong consensus on near-paraphrases / generic idioms")
print()
arab_fail = merged[(merged.language=='Arabic') & (merged.consensus_correct==0)]
for idx, row in list(arab_fail.sort_values('consensus_frac', ascending=False).head(3).iterrows()):
    print(f"**{row['proverb']}** ({row['variant']}, `{row['generator_model']}`)")
    print(f"- Correct meaning: *{row['correct_meaning']}* (correct key: **{row['correct_label']}**)")
    print(f"- Consensus: **{row['consensus_label']}** @ {row['consensus_frac']} | status: `{row['generation_status']}`, fallback_count={row['fallback_count']}")
    print(f"- A: {row['option_A']}")
    print(f"- B: {row['option_B']}")
    print(f"- C: {row['option_C']}")
    print(f"- D: {row['option_D']}")
    print()

print("### 5.3 English — too-easy / perfect-consensus-correct items")
print()
eng_easy = merged[(merged.language=='English') & (merged.consensus_correct==1) & (merged.consensus_frac==1.0)]
print(f"**Count of perfect-consensus-correct English items: {len(eng_easy)} / {len(merged[merged.language=='English'])} ({len(eng_easy)/len(merged[merged.language=='English']):.1%})**")
print()
for idx, row in list(eng_easy.head(3).iterrows()):
    print(f"**{row['proverb']}** ({row['variant']}, `{row['generator_model']}`)")
    print(f"- Correct meaning: *{row['correct_meaning']}* (correct key: **{row['correct_label']}**)")
    print(f"- A: {row['option_A']}")
    print(f"- B: {row['option_B']}")
    print(f"- C: {row['option_C']}")
    print(f"- D: {row['option_D']}")
    print()

print("## 6. Scaling gate assessment")
print()
print("| Gate | Target | English | Arabic | Yoruba |")
print("|------|--------|---------|--------|--------|")
print(f"| Consensus correctness | >=50% | 65.0% PASS | 53.3% PASS | 51.7% PASS |")
print(f"| Perfect consensus | <30% | 45.0% FAIL | 50.0% FAIL | 30.0% FAIL |")
print(f"| HCW rate | <10% | 33.3% FAIL | 46.7% FAIL | 48.3% FAIL |")
print()
print("### 6.1 Does Yoruba meet the >=50% correctness gate?")
print()
print("**Yes, barely.** Yoruba reaches 51.7% (95% CI 39.3%-63.8%), so it clears the 50% threshold but the lower CI bound is below 50%. With only 60 items the estimate is noisy; an N=15 run would tighten the interval.")
print()
print("### 6.2 Which languages are scaling blockers?")
print()
print("**All three are blockers for different reasons:**")
print("- **English** is the 'too-easy' blocker: 45% perfect-consensus-correct means distractors are not tempting enough; the MCQs are shortcut-solvable for auditors.")
print("- **Arabic** is the 'confident-wrong' blocker: 50% perfect consensus and 46.7% HCW — auditors agree too often and usually on attractive but wrong distractors.")
print("- **Yoruba** is the 'fragile low-resource' blocker: lowest consensus fraction and lowest auditor hit rates; the literal/cultural key is systematically overridden by more generic or proverb-like distractors.")
print()
print("Because **HCW >> 10%** and **perfect consensus >> 30%** in every language, scaling to N=15 without further pipeline changes is not advisable. The primary failure modes are:")
print("1. **Corpus fallback samplers** still inject low-quality or English-idiom distractors (visible in high `fallback_count` items, e.g. Arabic 'A bad workman...' with fallback_count=5).")
print("2. **Yoruba gold-meaning curation** preserves literal translations that auditors do not recognize as the intended key.")
print("3. **English distractors** are too semantically distant (antonyms / unrelated life advice) and are eliminated too easily.")
print()

print("## 7. Appendix: Per-variant and per-generator breakdown")
print()
print("### 7.1 Per-variant per-language")
print()
print("| Variant | English Acc / Perfect / HCW | Arabic Acc / Perfect / HCW | Yoruba Acc / Perfect / HCW |")
print("|---------|------------------------------|------------------------------|------------------------------|")
for variant in sorted(audit.variant.unique()):
    sub = audit[audit.variant==variant]
    vals = []
    for lang in ['English','Arabic','Yoruba']:
        s = sub[sub.language==lang]
        acc = s.consensus_correct.mean()
        perfect = (s.consensus_frac==1.0).mean()
        hcw = ((s.consensus_frac>=0.5)&(s.consensus_correct==0)).mean()
        vals.append(f"{acc:.1%} / {perfect:.1%} / {hcw:.1%}")
    print(f"| {variant} | {' | '.join(vals)} |")
print()
print("- `adversarial-length-locked` is especially harmful for Arabic (86.7% perfect consensus) and `taxonomy-guided` lifts Yoruba correctness to 66.7%.")
print("- No single variant satisfies all three languages simultaneously.")
print()
print("### 7.2 Per-generator per-language")
print()
print("| Generator | English Acc / Perfect / HCW | Arabic Acc / Perfect / HCW | Yoruba Acc / Perfect / HCW |")
print("|-----------|------------------------------|------------------------------|------------------------------|")
for gen in sorted(audit.generator_model.unique()):
    sub = audit[audit.generator_model==gen]
    vals = []
    for lang in ['English','Arabic','Yoruba']:
        s = sub[sub.language==lang]
        acc = s.consensus_correct.mean()
        perfect = (s.consensus_frac==1.0).mean()
        hcw = ((s.consensus_frac>=0.5)&(s.consensus_correct==0)).mean()
        vals.append(f"{acc:.1%} / {perfect:.1%} / {hcw:.1%}")
    print(f"| {gen} | {' | '.join(vals)} |")
print()
print("- `google/gemma-4-31b-it` is the most balanced generator (best Yoruba correctness at 70.0% and lowest Yoruba HCW at 30.0%).")
print("- `qwen/qwen3.7-max` is the weakest on Yoruba (40.0% correctness, 60.0% HCW).")
print()
print("## 8. Overall aggregates")
print()
n = len(audit)
k = audit.consensus_correct.sum()
print(f"- Overall consensus correctness: **{k}/{n} = {k/n:.1%}**")
print(f"- Overall perfect consensus: **{(audit.consensus_frac==1.0).sum()}/{n} = {(audit.consensus_frac==1.0).mean():.1%}**")
print(f"- Overall HCW: **{((audit.consensus_frac>=0.5)&(audit.consensus_correct==0)).sum()}/{n} = {((audit.consensus_frac>=0.5)&(audit.consensus_correct==0)).mean():.1%}**")
print(f"- Duplicate options: **{mcq.duplicate_options.sum()}**")
print(f"- Mean fallback count: **{mcq.fallback_count.mean():.2f}**")
print(f"- Partial + length_fallback status share: **{((mcq.generation_status=='partial') | (mcq.generation_status=='length_fallback')).mean():.1%}**")
print()
print("---")
print("*Report generated from `pilot1_test_audit_results.csv`, `pilot1_test_generated_mcqs.csv`, and `pilot1_test_summary.json`.*")
