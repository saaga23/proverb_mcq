import pandas as pd, json, numpy as np, os, ast
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 60)

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

def fmt_pct(x): return f"{x*100:.2f}%" if pd.notna(x) else 'NA'

evalr['failed'] = evalr['predicted'].isna() | evalr['error'].notna()
valid = evalr[~evalr['failed']].copy()

sec('1. Row counts and completeness')
line('### Evaluation files')
line(f'- eval_results.csv: {evalr.shape[0]} rows, {evalr.shape[1]} columns')
line(f'- eval_results_progress.csv: {evalp.shape[0]} rows, {evalp.shape[1]} columns')
line(f'- Files are identical: {evalr.equals(evalp)}')
line('### Column null counts (eval_results)')
line(evalr.isna().sum().to_frame('null_count').to_markdown())
line('### Summary stats')
line(f'- summary_stats.csv: {sumstat.shape[0]} rows, {sumstat.shape[1]} columns')
line('Row categories by strategy and language:')
line(sumstat.groupby(['strategy','language']).size().reset_index(name='rows').to_markdown(index=False))
line('### MCQ files')
line(f'- mcqs_s1.csv: {s1.shape[0]} rows, {s1.shape[1]} columns')
line(f'- mcqs_s2.csv: {s2.shape[0]} rows, {s2.shape[1]} columns')
line(f'- mcqs_all.csv: {allm.shape[0]} rows, {allm.shape[1]} columns')
line(f'- Expected if 3 languages x 50 samples x 2 strategies = 300 MCQs; present = {allm.shape[0]}')

sec('2. Failure rates')
fail_total = evalr['failed'].sum()
line(f'- Overall failures: {fail_total} / {len(evalr)} ({fmt_pct(fail_total/len(evalr))})')
line('### Failure rate per model')
fm = evalr.groupby('model')['failed'].agg(['sum','count']).reset_index()
fm['failure_rate'] = fm['sum']/fm['count']
line(fm.to_markdown(index=False, floatfmt='.4f'))
line('### Failure rate per strategy')
fs = evalr.groupby('strategy')['failed'].agg(['sum','count']).reset_index()
fs['failure_rate'] = fs['sum']/fs['count']
line(fs.to_markdown(index=False, floatfmt='.4f'))
line('### Failure rate per language')
fl = evalr.groupby('language')['failed'].agg(['sum','count']).reset_index()
fl['failure_rate'] = fl['sum']/fl['count']
line(fl.to_markdown(index=False, floatfmt='.4f'))
line('### Failure rate per model x strategy x language')
fmsl = evalr.groupby(['model','strategy','language'])['failed'].agg(['sum','count']).reset_index()
fmsl['failure_rate'] = fmsl['sum']/fmsl['count']
line(fmsl.to_markdown(index=False, floatfmt='.4f'))
line('### Error type counts')
line(evalr['error'].value_counts(dropna=False).to_frame('count').to_markdown())

sec('3. Accuracy patterns')
line('### Overall accuracy (excluding failures)')
overall_acc = valid['match'].mean()
line(f'- Valid predictions: {len(valid)}; correct: {valid["match"].sum()}; accuracy = {fmt_pct(overall_acc)}')
line('### Accuracy per strategy (valid-only)')
acc_s = valid.groupby('strategy')['match'].agg(['sum','count','mean']).reset_index()
line(acc_s.to_markdown(index=False, floatfmt='.4f'))
line('### Accuracy per language (valid-only)')
acc_l = valid.groupby('language')['match'].agg(['sum','count','mean']).reset_index()
line(acc_l.to_markdown(index=False, floatfmt='.4f'))
line('### Accuracy per model (valid-only)')
acc_m = valid.groupby('model')['match'].agg(['sum','count','mean']).reset_index()
line(acc_m.to_markdown(index=False, floatfmt='.4f'))
line('### Accuracy per model x strategy x language (valid-only)')
acc_msl = valid.groupby(['model','strategy','language'])['match'].agg(['sum','count','mean']).reset_index()
line(acc_msl.to_markdown(index=False, floatfmt='.4f'))
line('### Overall success rate (all evaluations, failures count as wrong)')
evalr['success'] = evalr['match'].fillna(False)
osr = evalr.groupby('model')['success'].mean().reset_index()
line(osr.to_markdown(index=False, floatfmt='.4f'))

sec('4. Deduplication')
eval_key_dup = evalr.duplicated(subset=['sample_id','strategy','model']).sum()
line(f'- Duplicate evaluation keys (sample_id+strategy+model): {eval_key_dup}')
line(f'- Fully duplicate rows in eval_results: {evalr.duplicated().sum()}')
line(f'- Duplicate MCQ keys (sample_id+strategy) in mcqs_all: {allm.duplicated(subset=["sample_id","strategy"]).sum()}')
line(f'- Distinct sample_id values in mcqs_s1: {s1["sample_id"].nunique()}')
line(f'- Distinct sample_id values in mcqs_s2: {s2["sample_id"].nunique()}')
line(f'- Distinct sample_id across mcqs_all: {allm["sample_id"].nunique()}')
s1_ids = set(s1['sample_id'])
s2_ids = set(s2['sample_id'])
line(f'- S1 only sample_ids: {len(s1_ids - s2_ids)}, S2 only: {len(s2_ids - s1_ids)}, shared: {len(s1_ids & s2_ids)}')
for dfname, df in [('s1',s1),('s2',s2),('all',allm)]:
    dup = df.duplicated(subset=['language','source_proverb']).sum()
    line(f'- {dfname}: {dup} duplicate (language, source_proverb) pairs')

sec('5. Data quality')
line('### MCQ strategy counts by language')
line(pd.crosstab(allm['strategy'], allm['language'], margins=True).to_markdown())
line('### Fallbacks (S2 only)')
fb_s2 = s2.groupby('language')['fallback'].agg(['sum','count','mean']).reset_index()
fb_s2['fallback_rate'] = fb_s2['mean']
line(fb_s2[['language','sum','count','fallback_rate']].to_markdown(index=False, floatfmt='.4f'))
line(f'- Total S2 fallbacks: {s2["fallback"].sum()} / {len(s2)} ({fmt_pct(s2["fallback"].mean())})')
line('### gen_attempts distribution (S2)')
line(s2['gen_attempts'].value_counts(dropna=False).sort_index().to_frame('count').to_markdown())
line('### gen_info distribution (S2)')
line(s2['gen_info'].value_counts(dropna=False).to_frame('count').to_markdown())

def normalize(t):
    return str(t).replace('�', '').replace('’',"'").replace('‘',"'").strip().lower()
allm['gold_norm'] = allm['gold'].apply(normalize)
letter_to_choice = {'A':'Choice_A','B':'Choice_B','C':'Choice_C','D':'Choice_D'}
allm['choice_for_answer_norm'] = allm.apply(lambda r: normalize(r[letter_to_choice[str(r['Answer']).strip().upper()]]), axis=1)
allm['answer_matches_gold'] = allm['gold_norm'] == allm['choice_for_answer_norm']
mismatches = allm[~allm['answer_matches_gold']]
line(f'- MCQs where Answer letter does not map to gold text (after normalization): {len(mismatches)} / {len(allm)}')
if len(mismatches) > 0:
    line(mismatches[['sample_id','language','strategy','Answer','gold','choice_for_answer_norm']].head(10).to_markdown(index=False))

def safe_len(x):
    try:
        if isinstance(x, str):
            return len(ast.literal_eval(x))
        return len(x)
    except Exception:
        return np.nan
allm['distractor_count'] = allm['distractors'].apply(safe_len)
line('### Distractor counts')
line(allm['distractor_count'].value_counts(dropna=False).sort_index().to_frame('count').to_markdown())
line(f'- MCQs with distractor_count != 3: {(allm["distractor_count"] != 3).sum()}')
choice_cols = ['Choice_A','Choice_B','Choice_C','Choice_D']
allm['choice_unique'] = allm[choice_cols].apply(lambda r: len(set(str(v).strip().lower() for v in r)), axis=1)
line(f'- MCQs with duplicate choices: {(allm["choice_unique"] < 4).sum()}')
def gold_in_distractors(row):
    try:
        gold = str(row['gold']).strip().lower()
        dlist = ast.literal_eval(row['distractors']) if isinstance(row['distractors'], str) else row['distractors']
        return any(str(d).strip().lower() == gold for d in dlist)
    except Exception:
        return False
allm['gold_in_distractors'] = allm.apply(gold_in_distractors, axis=1)
line(f'- MCQs where gold appears in distractors: {allm["gold_in_distractors"].sum()}')
line('### Invalid predictions in eval_results')
valid_letters = set(['A','B','C','D'])
invalid_pred = evalr[~evalr['predicted'].isna() & ~evalr['predicted'].isin(valid_letters)]
line(f'- Predicted values not in A-D: {len(invalid_pred)}')

sec('6. Pipeline state')
line('```json')
line(json.d
