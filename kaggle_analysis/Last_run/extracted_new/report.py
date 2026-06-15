import pandas as pd, json, numpy as np, os, ast
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

evalr = pd.read_csv('eval_results.csv')
evalp = pd.read_csv('eval_results_progress.csv')
sumstat = pd.read_csv('summary_stats.csv')
s1 = pd.read_csv('mcqs_s1.csv')
s2 = pd.read_csv('mcqs_s2.csv')
allm = pd.read_csv('mcqs_all.csv')
with open('pipeline_state.json') as f:
    state = json.load(f)

report = []
def sec(title): report.append('\n## ' + title)
def line(s): report.append(s)
def pct(x): return f"{x*100:.2f}%" if pd.notna(x) else 'NA'

evalr['failed'] = evalr['predicted'].isna() | evalr['error'].notna()
valid = evalr[~evalr['failed']].copy()

sec('1. Row counts and completeness')
line(f"eval_results.csv: {evalr.shape[0]} rows x {evalr.shape[1]} cols")
line(f"eval_results_progress.csv: {evalp.shape[0]} rows; identical to eval_results: {evalr.equals(evalp)}")
line('Column null counts in eval_results:')
line(evalr.isna().sum().to_frame('null_count').to_markdown())
line(f"summary_stats.csv: {sumstat.shape[0]} rows x {sumstat.shape[1]} cols")
line('Rows per strategy-language in summary_stats:')
line(sumstat.groupby(['strategy','language']).size().reset_index(name='rows').to_markdown(index=False))
line(f"mcqs_s1.csv: {s1.shape[0]}; mcqs_s2.csv: {s2.shape[0]}; mcqs_all.csv: {allm.shape[0]}")
line(f"Expected MCQs = 300; actual = {allm.shape[0]}; missing = {300-allm.shape[0]}")

sec('2. Failure rates')
fail_total = evalr['failed'].sum()
line(f"Overall failures: {fail_total}/{len(evalr)} ({pct(fail_total/len(evalr))})")
line('Per model:')
line(evalr.groupby('model')['failed'].agg(['sum','count']).assign(failure_rate=lambda x:x['sum']/x['count']).to_markdown(index=False, floatfmt='.4f'))
line('Per strategy:')
line(evalr.groupby('strategy')['failed'].agg(['sum','count']).assign(failure_rate=lambda x:x['sum']/x['count']).to_markdown(index=False, floatfmt='.4f'))
line('Per language:')
line(evalr.groupby('language')['failed'].agg(['sum','count']).assign(failure_rate=lambda x:x['sum']/x['count']).to_markdown(index=False, floatfmt='.4f'))
line('Per model x strategy x language:')
line(evalr.groupby(['model','strategy','language'])['failed'].agg(['sum','count']).assign(failure_rate=lambda x:x['sum']/x['count']).to_markdown(index=False, floatfmt='.4f'))
line('Error value counts:')
line(evalr['error'].value_counts(dropna=False).to_frame('count').to_markdown())

sec('3. Accuracy patterns')
line(f"Overall valid accuracy: {valid['match'].sum()}/{len(valid)} = {pct(valid['match'].mean())}")
line('Accuracy per strategy (valid-only):')
line(valid.groupby('strategy')['match'].agg(['sum','count','mean']).to_markdown(index=False, floatfmt='.4f'))
line('Accuracy per language (valid-only):')
line(valid.groupby('language')['match'].agg(['sum','count','mean']).to_markdown(index=False, floatfmt='.4f'))
line('Accuracy per model (valid-only):')
line(valid.groupby('model')['match'].agg(['sum','count','mean']).to_markdown(index=False, floatfmt='.4f'))
line('Accuracy per model x strategy x language (valid-only):')
line(valid.groupby(['model','strategy','language'])['match'].agg(['sum','count','mean']).to_markdown(index=False, floatfmt='.4f'))
line('Overall success rate (failures count as wrong):')
evalr['success'] = evalr['match'].fillna(False)
line(evalr.groupby('model')['success'].mean().reset_index(name='overall_success_rate').to_markdown(index=False, floatfmt='.4f'))

sec('4. Deduplication')
line(f"Duplicate eval keys (sample_id+strategy+model): {evalr.duplicated(subset=['sample_id','strategy','model']).sum()}")
line(f"Fully duplicate eval rows: {evalr.duplicated().sum()}")
line(f"Duplicate MCQ keys (sample_id+strategy): {allm.duplicated(subset=['sample_id','strategy']).sum()}")
line(f"Distinct sample_id: s1={s1['sample_id'].nunique()}, s2={s2['sample_id'].nunique()}, all={allm['sample_id'].nunique()}")
s1_ids=set(s1['sample_id']); s2_ids=set(s2['sample_id'])
line(f"Sample_id overlap: S1 only {len(s1_ids-s2_ids)}, S2 only {len(s2_ids-s1_ids)}, shared {len(s1_ids&s2_ids)}")
for name,df in [('s1',s1),('s2',s2),('all',allm)]:
    line(f"{name} duplicate (language,source_proverb) pairs: {df.duplicated(subset=['language','source_proverb']).sum()}")

sec('5. Data quality')
line('MCQ counts by strategy and language:')
line(pd.crosstab(allm['strategy'], allm['language'], margins=True).to_markdown())
line('Fallbacks in S2 by language:')
fb=s2.groupby('language')['fallback'].agg(['sum','count']).assign(fallback_rate=lambda x:x['sum']/x['count'])
line(fb.to_markdown(index=False, floatfmt='.4f'))
line(f"Total S2 fallbacks: {s2['fallback'].sum()}/{len(s2)} ({pct(s2['fallback'].mean())})")
line('gen_attempts distribution (S2):')
line(s2['gen_attempts'].value_counts(dropna=False).sort_index().to_frame('count').to_markdown())
line('gen_info distribution (S2):')
line(s2['gen_info'].value_counts(dropna=False).to_frame('count').to_markdown())

def norm(t): return str(t).replace('�','').replace('’',"'").replace('‘',"'").strip().lower()
allm['gold_norm']=allm['gold'].apply(norm)
letter={'A':'Choice_A','B':'Choice_B','C':'Choice_C','D':'Choice_D'}
allm['choice_ans_norm']=allm.apply(lambda r: norm(r[letter[str(r['Answer']).strip().upper()]]), axis=1)
allm['answer_ok']=allm['gold_norm']==allm['choice_ans_norm']
mm=allm[~allm['answer_ok']]
line(f"MCQs where Answer letter does not map to gold text: {len(mm)}/{len(allm)}")
if len(mm): line(mm[['sample_id','language','strategy','Answer','gold','choice_ans_norm']].head(10).to_markdown(index=False))

def dlen(x):
    try: return len(ast.literal_eval(x)) if isinstance(x,str) else len(x)
    except: return np.nan
allm['dcount']=allm['distractors'].apply(dlen)
line('Distractor counts:')
line(allm['dcount'].value_counts(dropna=False).sort_index().to_frame('count').to_markdown())
line(f"MCQs with distractor_count != 3: {(allm['dcount']!=3).sum()}")
cols=['Choice_A','Choice_B','Choice_C','Choice_D']
allm['uniq_choices']=allm[cols].apply(lambda r: len({str(v).strip().lower() for v in r}), axis=1)
line(f"MCQs with duplicate choices: {(allm['uniq_choices']<4).sum()}")
def gold_in_d(row):
    try:
        g=str(row['gold']).strip().lower()
        ds=ast.literal_eval(row['distractors']) if isinstance(row['distractors'],str) else row['distractors']
        return any(str(d).strip().lower()==g for d in ds)
    except: return False
allm['gold_in_d']=allm.apply(gold_in_d,axis=1)
line(f"MCQs where gold appears in distractors: {allm['gold_in_d'].sum()}")
line(f"Predicted values not in A-D: {evalr.loc[~evalr['predicted'].isna()&~evalr['predicted'].isin(['A','B','C','D'])].shape[0]}")

sec('6. Pipeline state')
line('```json')
line(json.dumps(state, indent=2))
line('```')
line(f"exhausted={state['exhausted']}; global_key_index={state['global_key_index']}; timestamp={state['timestamp']}; global_consecutive_failures={state['global_consecutive_failures']}")
line('Client states:')
line(pd.DataFrame(state['client_states']).T.reset_index().rename(columns={'index':'model'}).to_markdown(index=False, floatfmt='.1f'))
line('Evaluation rows per model:')
line(evalr['model'].value_counts().to_frame('eval_rows').to_markdown())
line('Note: qwen total_calls (522) exceeds its eval rows (300), indicating qwen was also used for generation.')

sec('7. Summary stats cross-check')
def recomp(df):
    return df.groupby(['strategy','language','model']).apply(lambda x: pd.Series({
        'total_n':len(x),'valid_n':(~x['failed']).sum(),'failure_n':x['failed'].sum(),
        'failure_rate':x['failed'].mean(),
        'accuracy':x.loc[~x['failed'],'match'].mean() if (~x['failed']).any() else np.nan,
        'overall_success_rate':x['match'].fillna(False).mean()})).reset_index()
r=recomp(evalr)
det=sumstat[(sumstat['model']!='ALL')&(sumstat['language']!='ALL')].copy()
c=det.merge(r, on=['strategy','language','model'], suffixes=('_summary','_recomputed'))
fields=['total_n','valid_n','failure_n','failure_rate','accuracy','overall_success_rate']
diffs=[]
for f in fields:
    diff=(c[f+'_summary']-c[f+'_recomputed']).abs().max()
    diffs.append((f,diff))
line('Max absolute difference between summary_stats and recomputed from eval_results:')
line(pd.DataFrame(diffs,columns=['metric','max_abs_diff']).to_markdown(index=False,floatfmt='.6f'))
line('Recomputed per-group values:')
line(r.to_markdown(index=False,floatfmt='.4f'))
line('Strategy overall recomputed:')
line(evalr.groupby('strategy').apply(lambda x: pd.Series({
    'total_n':len(x),'valid_n':(~x['failed']).sum(),'failure_n':x['failed'].sum(),
    'failure_rate':x['failed'].mean(),
    'accuracy':x.loc[~x['failed'],'match'].mean(),
    'overall_success_rate':x['match'].fillna(False).mean()})).reset_index().to_markdown(index=False,floatfmt='.4f'))
line('Summary ALL rows:')
line(sumstat[(sumstat['model']=='ALL')&(sumstat['language']=='ALL')][['strategy','total_n','valid_n','failure_n','failure_rate','accuracy','overall_success_rate']].to_markdown(index=False,floatfmt='.4f'))

sec('8. Anomalies')
pred_pivot=evalr.pivot_table(index=['sample_id','strategy','language'],columns='model',values='predicted',aggfunc='first')
unanimous=pred_pivot[(pred_pivot.nunique(axis=1)==1)&(~pred_pivot.isna().any(axis=1))]
line(f"MCQs where all 3 models gave same letter: {len(unanimous)}/{len(pred_pivot)}")
correct_map=valid.set_index(['sample_id','strategy','language','model'])['match']
all_correct=[]; all_wrong=[]
for idx,row in unanimous.iterrows():
    cs=[]
    for m in ['llama33-70b','gptoss120b','qwen3-32b']:
        try: cs.append(correct_map.loc[(*idx,m)])
        except KeyError: cs.append(False)
    if all(cs): all_correct.append(idx)
    elif not any(cs): all_wrong.append(idx)
line(f"  Unanimous and all correct: {len(all_correct)}; all wrong: {len(all_wrong)}")
perf=valid.groupby(['model','strategy','language'])['match'].mean().reset_index()
perf=perf[perf['match']==1.0]
line(f"Perfect accuracy groups (model x strategy x language): {len(perf)}")
if len(perf): line(perf.to_markdown(index=False,floatfmt='.4f'))
zero=valid.groupby(['model','strategy','language'])['match'].mean().reset_index()
zero=zero[zero['match']==0.0]
line(f"Zero accuracy groups (model x strategy x language): {len(zero)}")
if len(zero): line(zero.to_markdown(index=False,floatfmt='.4f'))
line('gptoss-120b anomaly: high failure rates (Arabic 48%/44%, Yoruba 80%/90% S1/S2) but high accuracy when it responds (S1 0.977, S2 0.937).')
empty_no_err=evalr[(evalr['raw_response'].isna()|(evalr['raw_response']==''))&evalr['error'].isna()]
line(f"Empty raw_response with no error: {len(empty_no_err)}")
bad_raw=valid[valid['predicted'].astype(str)!=valid['raw_response'].astype(str)]
line(f"Valid rows where predicted != raw_response: {len(bad_raw)}")

sec('9. Comparison with expected')
line(f"Expected evaluations: 900 (300 MCQs x 3 models)")
line(f"Actual evaluations: {len(evalr)}; missing: {900-len(evalr)}")
prev_exists=os.path.isdir('../extracted')
line(f"Previous extracted/ exists: {prev_exists}")
if not prev_exists:
    line('No previous extracted/ directory found; comparison not possible.')

sec('10. Yoruba S2 quality')
line('Fallbacks by language (S2):')
line(fb.to_markdown(index=False,floatfmt='.4f'))
yor_s2=s2[s2['language']=='Yoruba']
line(f"Yoruba S2 MCQs: {len(yor_s2)}; fallbacks: {yor_s2['fallback'].sum()} ({pct(yor_s2['fallback'].mean())}); generated: {(~yor_s2['fallback']).sum()}")
line('Yoruba S2 gen_attempts distribution:')
line(yor_s2['gen_attempts'].value_counts(dropna=False).sort_index().to_frame('count').to_markdown())
line('Yoruba S2 gen_info distribution:')
line(yor_s2['gen_info'].value_counts(dropna=False).to_frame('count').to_markdown())
line('Yoruba accuracy S1 vs S2 (valid-only):')
line(valid[valid['language']=='Yoruba'].groupby('strategy')['match'].agg(['sum','count','mean']).to_markdown(index=False,floatfmt='.4f'))
line('Yoruba failure rates S1 vs S2:')
line(evalr[evalr['language']=='Yoruba'].groupby('strategy')['failed'].agg(['sum','count']).assign(failure_rate=lambda x:x['sum']/x['count']).to_markdown(index=False,floatfmt='.4f'))
line('Yoruba S2 per-model valid accuracy:')
line(valid[(valid['language']=='Yoruba')&(valid['strategy']=='S2')].groupby('model')['match'].agg(['sum','count','mean']).to_markdown(index=False,floatfmt='.4f'))

sec('Appendix: Raw distributions')
line('Predicted letter distribution:')
line(evalr['predicted'].value_counts(dropna=False).to_frame('count').to_markdown())
line('Match distribution:')
line(evalr['match'].value_counts(dropna=False).to_frame('count').to_markdown())
line('Language x strategy counts in eval_results:')
line(pd.crosstab(evalr['language'],evalr['strategy'],margins=True).to_markdown())

with open('../analysis_report_extracted_new.md','w',encoding='utf-8') as f:
    f.write('\n'.join(report))
print('\n'.join(report))
print('\n--- Report saved to ../analysis_report_extracted_new.md ---')
