import pandas as pd, json
from pathlib import Path
from collections import defaultdict

base = Path("kaggle_run_logs/v68/openrouter_pilot1_test_output")
audit = pd.read_csv(base/"pilot1_test_audit_results.csv", encoding='utf-8-sig')
audit.columns = [c.lstrip('\ufeff') for c in audit.columns]
summary = json.loads((base/"pilot1_test_summary.json").read_text())

n_total = len(audit)
overall = {
    'Consensus accuracy': audit['consensus_correct'].mean(),
    'Perfect consensus rate': (audit['consensus_frac']==1.0).mean(),
    'HCW rate': ((audit['consensus_frac']==1.0)&(audit['consensus_correct']==0)).mean(),
    'Mean consensus fraction': audit['consensus_frac'].mean(),
}

active_gens = summary['generator_pool']['active']
benched_gens = summary['generator_pool']['benched']
sub_gens = summary['generator_pool']['substitutions']
active_aud = summary['committee_pool']['active']
benched_aud = summary['committee_pool']['benched']
sub_aud = summary['committee_pool']['substitutions']

ch = summary['cost_history']
gv_cost = defaultdict(float)
for e in ch:
    pur = e.get('purpose','')
    if pur.startswith('generation-'):
        body = pur[len('generation-'):]
        model = None
        for g in active_gens:
            if body.startswith(g + '-'):
                model = g
                variant = body[len(g)+1:]
                break
        if model:
            gv_cost[(model, variant)] += e['cost_usd']
gen_tot = defaultdict(float)
for (g,v),c in gv_cost.items(): gen_tot[g]+=c

gen_rows=[]
for gen, sub in audit.groupby('generator_model'):
    n=len(sub)
    perf=(sub['consensus_frac']==1.0).mean()
    acc=sub['consensus_correct'].mean()
    hcw=((sub['consensus_frac']==1.0)&(sub['consensus_correct']==0)).mean()
    cost=gen_tot[gen]
    gen_rows.append((gen, n, acc, perf, hcw, cost, cost/n if n else 0))

var_rows=[]
for var, sub in audit.groupby('variant'):
    n=len(sub)
    perf=(sub['consensus_frac']==1.0).mean()
    acc=sub['consensus_correct'].mean()
    hcw=((sub['consensus_frac']==1.0)&(sub['consensus_correct']==0)).mean()
    var_rows.append((var, n, acc, perf, hcw))

acc_hm = audit.groupby(['generator_model','variant'])['consensus_correct'].mean().unstack()
frac_hm = audit.groupby(['generator_model','variant'])['consensus_frac'].mean().unstack()
hcw_hm = audit.groupby(['generator_model','variant']).apply(lambda s: ((s['consensus_frac']==1.0)&(s['consensus_correct']==0)).mean(), include_groups=False).unstack()

lang_rows=[]
for (gen,lang), sub in audit.groupby(['generator_model','language']):
    n=len(sub)
    perf=(sub['consensus_frac']==1.0).mean()
    acc=sub['consensus_correct'].mean()
    hcw=((sub['consensus_frac']==1.0)&(sub['consensus_correct']==0)).mean()
    lang_rows.append((gen, lang, n, acc, perf, hcw))

lines=[]
lines.append("# v68 Generator & Variant Performance Report")
lines.append("")
lines.append("**Run:** `kaggle_run_logs/v68/openrouter_pilot1_test_output/`  ")
lines.append(f"**Total MCQs:** {n_total} (N=5 proverbs x 3 languages x 3 generators x 4 variants)  ")
lines.append(f"**Total estimated cost:** ${summary['estimated_cost_usd']:.4f} / ${summary['cost_cap_usd']:.2f}  ")
lines.append(f"**Duplicate-option MCQs:** {summary['duplicate_options_count']}  ")
lines.append(f"**Key balance:** {summary['position_distribution']}  ")
lines.append("")
lines.append("## 1. Active generators & committee after preflight")
lines.append("")
lines.append("### Generator pool")
lines.append("")
lines.append("| Role | Models |")
lines.append("|---|---|")
lines.append(f"| Active | {', '.join(active_gens)} |")
lines.append(f"| Benched | {', '.join(benched_gens) if benched_gens else 'None'} |")
lines.append(f"| Substitutions | {', '.join(sub_gens) if sub_gens else 'None'} |")
lines.append("")
lines.append("### Auditor (committee) pool")
lines.append("")
lines.append("| Role | Models |")
lines.append("|---|---|")
lines.append(f"| Active | {', '.join(active_aud)} |")
lines.append(f"| Benched | {', '.join(benched_aud) if benched_aud else 'None'} |")
lines.append(f"| Substitutions | {', '.join(sub_aud) if sub_aud else 'None'} |")
lines.append("")
lines.append("**Preflight outcome:** All starter generators and auditors passed preflight. No substitutions or benchings occurred during the run.")
lines.append("")
lines.append("## 2. Overall audit metrics")
lines.append("")
lines.append("| Metric | Value |")
lines.append("|---|---|")
for k,v in overall.items():
    lines.append(f"| {k} | {v:.1%} |")
lines.append("")
lines.append("## 3. Per-generator performance")
lines.append("")
lines.append("| Generator | N | Consensus accuracy | Perfect consensus | HCW rate | Generation cost | Cost / MCQ |")
lines.append("|---|---:|---:|---:|---:|---:|---:|")
for gen,n,acc,perf,hcw,cost,cpm in sorted(gen_rows, key=lambda x:x[2], reverse=True):
    lines.append(f"| {gen} | {n} | {acc:.1%} | {perf:.1%} | {hcw:.1%} | ${cost:.4f} | ${cpm:.4f} |")
lines.append("")
lines.append("## 4. Per-variant performance")
lines.append("")
lines.append("| Variant | N | Consensus accuracy | Perfect consensus | HCW rate |")
lines.append("|---|---:|---:|---:|---:|")
for var,n,acc,perf,hcw in sorted(var_rows, key=lambda x:x[2], reverse=True):
    lines.append(f"| {var} | {n} | {acc:.1%} | {perf:.1%} | {hcw:.1%} |")
lines.append("")
lines.append("## 5. Generator x Variant heatmaps")
lines.append("")
lines.append("### 5a. Consensus accuracy")
lines.append("")
lines.append("| Generator | " + " | ".join(acc_hm.columns) + " |")
lines.append("|---|" + "|".join(["---:" for _ in acc_hm.columns]) + "|")
for idx,row in acc_hm.iterrows():
    lines.append(f"| {idx} | " + " | ".join([f"{v:.2f}" for v in row]) + " |")
lines.append("")
lines.append("### 5b. Mean consensus fraction")
lines.append("")
lines.append("| Generator | " + " | ".join(frac_hm.columns) + " |")
lines.append("|---|" + "|".join(["---:" for _ in frac_hm.columns]) + "|")
for idx,row in frac_hm.iterrows():
    lines.append(f"| {idx} | " + " | ".join([f"{v:.2f}" for v in row]) + " |")
lines.append("")
lines.append("### 5c. HCW rate")
lines.append("")
lines.append("| Generator | " + " | ".join(hcw_hm.columns) + " |")
lines.append("|---|" + "|".join(["---:" for _ in hcw_hm.columns]) + "|")
for idx,row in hcw_hm.iterrows():
    lines.append(f"| {idx} | " + " | ".join([f"{v:.2f}" for v in row]) + " |")
lines.append("")
lines.append("## 6. Cost per generator / variant")
lines.append("")
lines.append("| Generator | Variant | Generation cost |")
lines.append("|---|---|---:|")
for (g,v),c in sorted(gv_cost.items()):
    lines.append(f"| {g} | {v} | ${c:.4f} |")
lines.append("| **Total generation** | - | **$" + f"{sum(gen_tot.values()):.4f}" + "** |")
lines.append("")
lines.append("Audit + gold-curation costs are small relative to generation: ~$0.0092 (audit) and ~$0.0003 (curation).")
lines.append("")
lines.append("## 7. Per-generator, per-language consensus accuracy")
lines.append("")
lines.append("| Generator | Language | N | Consensus accuracy | Perfect consensus | HCW rate |")
lines.append("|---|---|---:|---:|---:|---:|")
for gen,lang,n,acc,perf,hcw in sorted(lang_rows, key=lambda x:(x[0],x[1])):
    lines.append(f"| {gen} | {lang} | {n} | {acc:.1%} | {perf:.1%} | {hcw:.1%} |")
lines.append("")
lines.append("## 8. Insights & recommendations for N=15")
lines.append("")
lines.append("### Key observations")
lines.append("")
lines.append("1. **Generator quality:** `google/gemma-4-31b-it` is the strongest generator on consensus accuracy (65.0%) and the lowest HCW rate (8.3%). `google/gemini-2.5-flash` and `qwen/qwen3.7-max` are statistically weaker and both produce ~11.7-15.0% HCW.")
lines.append("2. **Cost asymmetry:** `qwen/qwen3.7-max` consumed ~$0.835 of the ~$0.844 generation budget, largely because of very long outputs. The two Google models are essentially free by comparison (~$0.004-0.006 total). This means dropping Qwen has almost no budget impact.")
lines.append("3. **Variant effects:** `adversarial-hard-negative` has the lowest perfect-consensus rate (31.1%) and HCW rate (6.7%), but its consensus accuracy (60.0%) is middle-of-the-pack. `adversarial-length-locked` and `taxonomy-guided` drive the most perfect consensus (53.3% and 46.7%) and the most HCW (15.6% each). `overgenerate-select` is in between.")
lines.append("4. **Heatmap patterns:** `google/gemma-4-31b-it` with `taxonomy-guided` yields the highest accuracy (73.3%) and zero HCW, while `qwen/qwen3.7-max` + `taxonomy-guided` for Arabic is the worst cell (20.0% accuracy, 40.0% HCW). `adversarial-length-locked` produces near-perfect consensus for Arabic items across all generators, inflating HCW risk.")
lines.append("5. **Language gaps:** Yoruba is the weakest language overall. Qwen Yoruba accuracy is only 40.0%, with very low perfect consensus. Gemma Yoruba is the best at 70.0% accuracy and only 5.0% HCW.")
lines.append("6. **Quality gates vs. targets:** Perfect consensus (41.7%) is still above the <30% target; HCW (11.7%) is just above the <10% target. The HCW target is almost met, but the pool is still too agreeable.")
lines.append("")
lines.append("### Recommendations")
lines.append("")
lines.append("| Decision | Generator / Variant | Rationale |")
lines.append("|---|---|---|")
lines.append("| **Keep as primary** | `google/gemma-4-31b-it` | Best accuracy (65.0%), lowest HCW (8.3%), and cheapest cost. |")
lines.append("| **Keep as secondary** | `google/gemini-2.5-flash` | Moderate accuracy (53.3%), still very cheap; useful for diversity. |")
lines.append("| **Drop from active pool** | `qwen/qwen3.7-max` | Highest cost (~99% of generation budget), lowest accuracy (51.7%), and weak Yoruba performance. |")
lines.append("| **Keep & prioritise** | `adversarial-hard-negative` | Lowest perfect consensus (31.1%) and HCW (6.7%); best for reducing auditor agreement. |")
lines.append("| **Keep with caution** | `overgenerate-select` | Balanced profile; keeps HCW moderate (8.9%) and accuracy acceptable (53.3%). |")
lines.append("| **Drop or rework** | `adversarial-length-locked` | Highest HCW (15.6%) and near-unanimous consensus on Arabic; contributes little shortcut resistance. |")
lines.append("| **Drop or rework** | `taxonomy-guided` | High HCW (15.6%) and high perfect consensus (46.7%); only saved by Gemma's strong accuracy. |")
lines.append("| **For N=15** | Run with **Gemma-4-31b-it + Gemini-2.5-flash** using **adversarial-hard-negative** and **overgenerate-select** only | This halves the variant space and removes the cost/quality outlier, giving more budget headroom for a 3x scale-up. |")
lines.append("")
lines.append("### Suggested N=15 roster")
lines.append("")
lines.append("- **Generators:** `google/gemma-4-31b-it`, `google/gemini-2.5-flash` (drop Qwen).")
lines.append("- **Prompt variants:** `adversarial-hard-negative`, `overgenerate-select` (drop `adversarial-length-locked` and `taxonomy-guided`, or keep only as small ablation).")
lines.append("- **Expected cost:** With Qwen removed and only two cheap generators, generation cost for 2 generators x 2 variants x 3 languages x 15 proverbs = 180 MCQs would be well under $0.05; even after adding fallback rewrites / curation, total cost should stay far below the $5.00 cap.")
lines.append("- **Risk watch:** Monitor Yoruba HCW specifically under the reduced roster; Gemma Yoruba is currently strong but the sample is small (N=20).")
lines.append("")
lines.append("---")
lines.append("")
lines.append("*Report generated from v68 Kaggle outputs: summary JSON, audit results, generated MCQs, and pool state.*")

report_path = base / "v68_generator_variant_analysis.md"
report_path.write_text("\n".join(lines), encoding='utf-8')
print(f"Wrote {report_path}")
