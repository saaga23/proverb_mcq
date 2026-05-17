"""
pilot_v2.py — ProverbGap Hardened MCQ Pipeline
==============================================
Runs a hardened pilot of the MCQ generation and shortcut audit using:
1. Strategy 1: In-Domain Negative Proverb Sampling (Pure human text).
2. Strategy 2: LLM Generation + Style-Paraphrasing of Correct Answer.
3. A 5-Model EMNLP Reviewer Committee blind shortcut audit (Llama 3.1 8B, Gemma 2 9B, Mixtral 8x7B, Llama 3.3 70B, Llama 3.1 70B).

Usage:
  python pilot_v2.py --groq-key <KEY> --task a --n 30 --data-dir "original_data"
"""

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description='ProverbGap Hardened MCQ Pipeline')
parser.add_argument('--groq-key',  default=os.environ.get('GROQ_API_KEY',''),
                    help='Groq API key (or set GROQ_API_KEY env var)')
parser.add_argument('--task',      default='a', choices=['a','b'],
                    help='a=literal, b=cultural (default: a)')
parser.add_argument('--n',         default=30, type=int,
                    help='Items per language (default: 30)')
parser.add_argument('--data-dir',  default='original_data',
                    help='Folder containing the cleaned CSV files (default: original_data)')
parser.add_argument('--out',       default='pilot_v2_results',
                    help='Output folder (default: pilot_v2_results)')
parser.add_argument('--gen-model', default='llama-3.3-70b-versatile',
                    help='Model for distractor generation (Strategy 2)')
args = parser.parse_args()

if not args.groq_key:
    print('ERROR: Provide --groq-key or set GROQ_API_KEY env var')
    sys.exit(1)

try:
    import pandas as pd
    from groq import Groq
except ImportError:
    print('ERROR: Run: pip install groq pandas')
    sys.exit(1)

client = Groq(api_key=args.groq_key)
OUT = Path(args.out)
OUT.mkdir(exist_ok=True)
DATA = Path(args.data_dir)
random.seed(42)

LANGUAGES = ['Yoruba', 'Arabic', 'English']

COMMITTEE_MODELS = [
    'llama-3.1-8b-instant',
    'gemma2-9b-it',
    'mixtral-8x7b-32768',
    'llama-3.3-70b-versatile',
    'llama-3.1-70b-versatile'
]

print(f'\n{"="*60}')
print(f'  ProverbGap Hardened MCQ Pipeline')
print(f'  Task: {"B (Cultural)" if args.task=="b" else "A (Literal)"}')
print(f'  Items per language (N): {args.n}')
print(f'  Data dir: {DATA}')
print(f'  Gen model (Strategy 2): {args.gen_model}')
print(f'  Reviewer Committee Models: {", ".join(COMMITTEE_MODELS)}')
print(f'{"="*60}\n')

# ── prompts ──────────────────────────────────────────────────────────────────

SYS_A_STRAT2 = (
    "You are a linguistic expert building a translation comprehension benchmark.\n"
    "Given a proverb and its correct English translation, you must generate 4 options written in the EXACT same style, tone, register, and length.\n"
    "Requirements:\n"
    "1. Option 1 MUST be a correct and natural paraphrase of the English translation.\n"
    "2. Options 2, 3, and 4 MUST be incorrect direct translations (introduce a subtle meaning shift: swap the subject/object, invert a condition, or change the consequence).\n"
    "3. All 4 options must sound equally natural to a native speaker. The blind evaluator should not be able to guess the correct answer based on length or phrasing style.\n"
    "Return ONLY a valid JSON list of 4 strings where the first element is the correct paraphrase: [\"correct_paraphrase\", \"distractor_1\", \"distractor_2\", \"distractor_3\"]"
)

SYS_B_STRAT2 = (
    "You are a cultural anthropology expert building a proverb reasoning benchmark.\n"
    "Given a proverb, its English translation, and its correct cultural meaning, you must generate 4 options written in the EXACT same style, tone, register, and length.\n"
    "Requirements:\n"
    "1. Option 1 MUST be a correct paraphrase of the cultural meaning.\n"
    "2. Options 2, 3, and 4 MUST be incorrect cultural interpretations (convey a completely different life lesson, social rule, or value, but sound equally plausible as ancient wisdom).\n"
    "3. All 4 options must be written in the same register. The blind evaluator should not be able to guess the correct answer based on length, tone, or style.\n"
    "Return ONLY a valid JSON list of 4 strings where the first element is the correct paraphrase: [\"correct_paraphrase\", \"distractor_1\", \"distractor_2\", \"distractor_3\"]"
)

def make_prompt_a(proverb, translation, lang):
    return (
        f'Proverb ({lang}): {proverb}\n'
        f'Correct English translation: {translation}\n\n'
        'Generate 4 options in a valid JSON list of strings (Option 1 correct paraphrase, Options 2-4 wrong translations).'
    )

def make_prompt_b(proverb, translation, cultural_meaning, lang):
    return (
        f'Proverb ({lang}): {proverb}\n'
        f'English translation: {translation}\n'
        f'Correct cultural meaning: {cultural_meaning}\n\n'
        'Generate 4 options in a valid JSON list of strings (Option 1 correct paraphrase, Options 2-4 wrong interpretations).'
    )

# ── API Caller with Backoff ───────────────────────────────────────────────────

def call_groq(sys_prompt, user_prompt, model, temperature=0.7, max_tokens=600):
    """Call Groq API with robust retry and error handling."""
    for attempt in range(6):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': sys_prompt},
                    {'role': 'user',   'content': user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e)
            print(f'  [API Attempt {attempt+1} Failed on {model}]: {err[:100]}')
            if 'rate_limit' in err.lower() or '429' in err:
                time.sleep(15 * (attempt + 1))
            else:
                time.sleep(3)
    return None

def parse_response_strat2(raw):
    """Parse JSON containing 4 options [correct_paraphrase, d1, d2, d3]."""
    if not raw:
        return None
    raw = re.sub(r'<reasoning>.*?</reasoning>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    raw = raw.strip()
    raw = re.sub(r'^```\w*\n?', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\n?```$', '', raw, flags=re.MULTILINE)
    raw = raw.strip()
    try:
        d = json.loads(raw)
        if isinstance(d, list) and len(d) >= 4:
            return [str(x).strip() for x in d[:4] if str(x).strip()]
    except json.JSONDecodeError:
        pass
    m = re.search(r'\[[\s\S]*?\]', raw)
    if m:
        try:
            d = json.loads(m.group())
            if isinstance(d, list) and len(d) >= 4:
                return [str(x).strip() for x in d[:4] if str(x).strip()]
        except json.JSONDecodeError:
            pass
    return None

def assemble_mcq(correct, distractors, seed):
    """Shuffle options deterministically."""
    rng = random.Random(seed)
    choices = list(distractors[:3]) + [correct]
    rng.shuffle(choices)
    labels = ['A', 'B', 'C', 'D']
    answer = labels[choices.index(correct)]
    choice_dict = {f'Choice_{l}': choices[i] for i, l in enumerate(labels)}
    return choice_dict, answer

# ── Load Data ─────────────────────────────────────────────────────────────────

dfs = {}
for lang in LANGUAGES:
    csv_path = DATA / f'{lang}_cleaned.csv'
    if not csv_path.exists():
        print(f'[SKIP] {lang}: {csv_path} not found')
        continue
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f'[SKIP] {lang}: Read error — {e}')
        continue
    
    col_map = {
        'Source_Text_Yo': 'source_proverb',
        'Source_Text_Mid': 'source_proverb',
        'Proverb': 'source_proverb',
        'Target_Text_En': 'proverb_en',
        'Translation': 'proverb_en',
        'Cultural_Context': 'correct_meaning',
        'Correct_Meaning': 'correct_meaning'
    }
    df = df.rename(columns=col_map)
    
    if lang == 'English' and 'correct_meaning' not in df.columns:
        df['correct_meaning'] = df['proverb_en']
        
    required = ['source_proverb', 'proverb_en', 'correct_meaning']
    df = df.dropna(subset=required).reset_index(drop=True)
    if 'sample_id' not in df.columns and 'Sample_ID' not in df.columns:
        df['sample_id'] = [f'{lang[:3].upper()}{str(i+1).zfill(4)}' for i in range(len(df))]
    
    dfs[lang] = df.sample(min(args.n, len(df)), random_state=42).reset_index(drop=True)
    print(f'Loaded {lang}: {len(dfs[lang])} samples from {csv_path.name}')

# ── GENERATION & EVALUATION LOOP ──────────────────────────────────────────────

all_results = {}

for strategy in ['Strategy_1', 'Strategy_2']:
    print(f'\n\n{"="*60}')
    print(f'  EXECUTING: {strategy}')
    print(f'{"="*60}')
    
    gen_rows = []
    
    for lang in LANGUAGES:
        df = dfs.get(lang)
        if df is None or df.empty:
            continue
            
        print(f'\n[{lang}] Generating distractors via {strategy}...')
        
        for idx, row in df.iterrows():
            proverb = str(row['source_proverb'])
            translation = str(row['proverb_en'])
            correct_meaning = str(row['correct_meaning'])
            target_text = correct_meaning if args.task == 'b' else translation
            
            if strategy == 'Strategy_1':
                # Pure human negative proverb sampling from the other rows
                candidates = df[df['sample_id'] != row['sample_id']]
                sampled_rows = candidates.sample(3, random_state=42 + idx)
                dists = [str(r['correct_meaning'] if args.task == 'b' else r['proverb_en']) for _, r in sampled_rows.iterrows()]
                correct_option = target_text
                
                choices, answer = assemble_mcq(correct_option, dists, 42 + idx)
                gen_rows.append({
                    'language': lang,
                    'sample_id': row.get('sample_id', f'{lang[:3]}{idx:04d}'),
                    'source_proverb': proverb,
                    'proverb_en': translation,
                    'correct_text': target_text,
                    **choices,
                    'Answer': answer
                })
            else:
                # LLM Generation with Style-Paraphrasing of Correct Answer
                sys_p = SYS_B_STRAT2 if args.task == 'b' else SYS_A_STRAT2
                user_p = make_prompt_b(proverb, translation, correct_meaning, lang) if args.task == 'b' else make_prompt_a(proverb, translation, lang)
                
                raw = call_groq(sys_p, user_p, model=args.gen_model)
                options = parse_response_strat2(raw)
                
                if not options or len(options) < 4:
                    print(f'  [PARSE FAIL] fallback to negative sampling for {row.get("sample_id","?")}')
                    # Fallback to negative sampling so we don't crash
                    candidates = df[df['sample_id'] != row['sample_id']]
                    sampled_rows = candidates.sample(3, random_state=42 + idx)
                    dists = [str(r['correct_meaning'] if args.task == 'b' else r['proverb_en']) for _, r in sampled_rows.iterrows()]
                    correct_option = target_text
                else:
                    correct_option = options[0]  # Paraphrased correct answer
                    dists = options[1:4]         # Hardened distractors
                    
                choices, answer = assemble_mcq(correct_option, dists, 42 + idx)
                gen_rows.append({
                    'language': lang,
                    'sample_id': row.get('sample_id', f'{lang[:3]}{idx:04d}'),
                    'source_proverb': proverb,
                    'proverb_en': translation,
                    'correct_text': correct_option,
                    **choices,
                    'Answer': answer
                })
                time.sleep(1.0) # stay under rate limits
                
            if (idx + 1) % 10 == 0:
                print(f'  {idx+1}/{len(df)} generated.')
                
    gen_df = pd.DataFrame(gen_rows)
    gen_path = OUT / f'pilot_v2_gen_{args.task}_{strategy.lower()}.csv'
    gen_df.to_csv(gen_path, index=False)
    print(f'Saved generated MCQ items to {gen_path}')
    
    # ── BLIND AUDIT WITH 5-MODEL COMMITTEE ────────────────────────────────────
    
    print(f'\nRunning Blind Shortcut Audit via 5-Model EMNLP Reviewer Committee...')
    
    target_type = "translation" if args.task == 'a' else "interpretation"
    audit_sys = f"Reply ONLY with A, B, C, or D. Guess the human {target_type}."
    
    # Store predictions for each model
    model_predictions = {model: [] for model in COMMITTEE_MODELS}
    
    for idx, row in gen_df.iterrows():
        user_aud = f"Which is correct?\\nA. {row['Choice_A']}\\nB. {row['Choice_B']}\\nC. {row['Choice_C']}\\nD. {row['Choice_D']}"
        
        for model in COMMITTEE_MODELS:
            pred_raw = call_groq(audit_sys, user_aud, model=model, temperature=0.0, max_tokens=5)
            pred = (pred_raw or '').strip().upper()[:1]
            if pred not in ['A', 'B', 'C', 'D']:
                pred = None
            model_predictions[model].append(pred)
            time.sleep(0.15)
            
        if (idx + 1) % 10 == 0:
            print(f'  Audited {idx+1}/{len(gen_df)} items...')
            
    # Add predictions to DataFrame
    audit_results = []
    for idx, row in gen_df.iterrows():
        votes = []
        item_res = {
            'language': row['language'],
            'sample_id': row['sample_id'],
            'correct_answer': row['Answer']
        }
        
        for model in COMMITTEE_MODELS:
            pred = model_predictions[model][idx]
            item_res[f'pred_{model}'] = pred
            item_res[f'hit_{model}'] = int(pred == row['Answer']) if pred else 0
            if pred:
                votes.append(pred)
                
        # Committee Consensus (Majority Vote)
        if votes:
            consensus = max(set(votes), key=votes.count)
        else:
            consensus = None
        item_res['pred_consensus'] = consensus
        item_res['hit_consensus'] = int(consensus == row['Answer']) if consensus else 0
        audit_results.append(item_res)
        
    audit_df = pd.DataFrame(audit_results)
    audit_path = OUT / f'pilot_v2_audit_{args.task}_{strategy.lower()}.csv'
    audit_df.to_csv(audit_path, index=False)
    
    # Compute Metrics per Language
    strategy_metrics = {}
    for lang in LANGUAGES:
        sub = audit_df[audit_df['language'] == lang]
        if sub.empty:
            continue
        lang_metrics = {}
        for model in COMMITTEE_MODELS:
            lang_metrics[model] = round(sub[f'hit_{model}'].mean() * 100, 1)
        lang_metrics['Consensus'] = round(sub['hit_consensus'].mean() * 100, 1)
        strategy_metrics[lang] = lang_metrics
        
    all_results[strategy] = strategy_metrics

# ── REPORTING ─────────────────────────────────────────────────────────────────

print(f'\n{"="*80}')
print(f'  FINAL EMNLP REVIEWER COMMITTEE BENCHMARK REPORT (N={args.n})')
print(f'{"="*80}')

for strategy in ['Strategy_1', 'Strategy_2']:
    print(f'\n>>> {strategy.upper()}:')
    print(f'  {"Language":<12} | ' + ' | '.join(f'{m[:10]:<10}' for m in COMMITTEE_MODELS) + ' | Consensus')
    print(f'  {"-"*95}')
    for lang in LANGUAGES:
        metrics = all_results[strategy].get(lang)
        if not metrics:
            continue
        row_str = f'  {lang:<12} | '
        row_str += ' | '.join(f'{metrics[m]:>9.1f}%' for m in COMMITTEE_MODELS)
        row_str += f' | {metrics["Consensus"]:>8.1f}%'
        
        # Check pass status (Consensus < 30%)
        status = '✅ PASS' if metrics["Consensus"] < 30.0 else ('🟡 REVIEW' if metrics["Consensus"] < 45.0 else '🔴 FAIL')
        row_str += f'  ({status})'
        print(row_str)
    print(f'  {"-"*95}')

print(f'\nReport saved to: {OUT}/')
print(f'{"="*80}\n')
