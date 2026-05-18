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
                    help='Groq API key (optional fallback)')
parser.add_argument('--task',      default='a', choices=['a','b'],
                    help='a=literal, b=cultural (default: a)')
parser.add_argument('--n',         default=30, type=int,
                    help='Items per language (default: 30)')
parser.add_argument('--data-dir',  default='original_data',
                    help='Folder containing the cleaned CSV files (default: original_data)')
parser.add_argument('--out',       default='pilot_v2_results',
                    help='Output folder (default: pilot_v2_results)')
parser.add_argument('--gen-model', default='llama-3.3-70b',
                    help='Model for distractor generation (Strategy 2)')
args = parser.parse_args()

try:
    import pandas as pd
except ImportError:
    print('ERROR: Run: pip install pandas requests')
    sys.exit(1)

import sqlite3
import hashlib
import requests

def _load_keys(names):
    keys = []
    # Try loading from kaggle_secrets
    try:
        from kaggle_secrets import UserSecretsClient
        s = UserSecretsClient()
        for name in names:
            try:
                k = s.get_secret(name)
                if k and k.strip() and k.strip() not in keys:
                    keys.append(k.strip())
            except:
                pass
    except:
        pass
    # Try loading from environment variables
    for name in names:
        k = os.environ.get(name, '').strip()
        if k and k not in keys:
            keys.append(k)
    return keys

# Load all 28 possible keys dynamically
CEREBRAS_KEYS = _load_keys(['CEREBRAS_API_KEY', 'CEREBRAS_API_KEY_2'])
SAMBANOVA_KEYS = _load_keys(['SAMBANOVA_API_KEY'])
NVIDIA_KEYS = _load_keys(['NVIDIA_API_KEY', 'NVIDIA_API_KEY_2', 'NVIDIA_API_KEY_3', 'NVIDIA_API_KEY_4'])
LLM7_KEYS = _load_keys(['LLM7_API_KEY', 'LLM7_API_KEY_2', 'LLM7_API_KEY_3'])
DEEPINFRA_KEYS = _load_keys(['DEEPINFRA_API_KEY'])
DEEPSEEK_KEYS = _load_keys(['DEEPSEEK_API_KEY'])
GROQ_KEYS = _load_keys(['GROQ_API_KEY'] + [f'GROQ_API_KEY_{i}' for i in range(2, 9)])
if args.groq_key and args.groq_key not in GROQ_KEYS:
    GROQ_KEYS.append(args.groq_key)

print(f"Loaded key pools: Cerebras={len(CEREBRAS_KEYS)}, SambaNova={len(SAMBANOVA_KEYS)}, Nvidia={len(NVIDIA_KEYS)}, LLM7={len(LLM7_KEYS)}, DeepInfra={len(DEEPINFRA_KEYS)}, DeepSeek={len(DEEPSEEK_KEYS)}, Groq={len(GROQ_KEYS)}")

OUT = Path(args.out)
OUT.mkdir(exist_ok=True)
DATA = Path(args.data_dir)
random.seed(42)

LANGUAGES = ['Yoruba', 'Arabic', 'English']

COMMITTEE_MODELS = [
    'llama-3.1-8b',
    'deepseek-r1',
    'gemma-2-9b',
    'mixtral-8x7b',
    'llama-3.3-70b'
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
    "4. CRITICAL: All 4 options MUST be of extremely similar length (within 10% of each other's character count). If Option 1 is short, distractors must be short. If Option 1 is long, distractors must be long. Avoid any length signature.\n"
    "Return ONLY a valid JSON list of 4 strings where the first element is the correct paraphrase: [\"correct_paraphrase\", \"distractor_1\", \"distractor_2\", \"distractor_3\"]"
)

SYS_B_STRAT2 = (
    "You are a cultural anthropology expert building a proverb reasoning benchmark.\n"
    "Given a proverb, its English translation, and its correct cultural meaning, you must generate 4 options written in the EXACT same style, tone, register, and length.\n"
    "Requirements:\n"
    "1. Option 1 MUST be a correct paraphrase of the cultural meaning.\n"
    "2. Options 2, 3, and 4 MUST be incorrect cultural interpretations (convey a completely different life lesson, social rule, or value, but sound equally plausible as ancient wisdom).\n"
    "3. All 4 options must be written in the same register. The blind evaluator should not be able to guess the correct answer based on length, tone, or style.\n"
    "4. CRITICAL: All 4 options MUST be of extremely similar length (within 10% of each other's character count). If Option 1 is short, distractors must be short. If Option 1 is long, distractors must be long. Avoid any length signature.\n"
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

class APICache:
    def __init__(self, db_path='.api_cache.sqlite'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response TEXT
                )
            ''')

    def _make_key(self, sys_p, user_p, model):
        hash_input = f"{sys_p}|||{user_p}|||{model}".encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()

    def get(self, sys_p, user_p, model):
        key = self._make_key(sys_p, user_p, model)
        cursor = self.conn.cursor()
        cursor.execute("SELECT response FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set(self, sys_p, user_p, model, response):
        key = self._make_key(sys_p, user_p, model)
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO cache (key, response) VALUES (?, ?)", (key, response))

cache = APICache()

# Rotator indices
_key_indices = {
    'cerebras': 0,
    'sambanova': 0,
    'nvidia': 0,
    'llm7': 0,
    'deepinfra': 0,
    'groq': 0,
    'deepseek': 0
}

# Individual Provider Callers
def call_cerebras(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.cerebras.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_sambanova(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.sambanova.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_nvidia(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_llm7(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.llm7.io/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_deepinfra(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_groq_api(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def call_deepseek(key, model_id, sys_p, user_p, max_tok, temp):
    resp = requests.post("https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model_id, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
              "temperature": temp, "max_tokens": max_tok}, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

# Unified Routing Map
PROVIDER_ROUTING = {
    'llama-3.1-8b': [
        ('groq',       'llama-3.1-8b-instant',             GROQ_KEYS),
        ('cerebras',  'llama3.1-8b',                      CEREBRAS_KEYS),
        ('sambanova',  'Meta-Llama-3.1-8B-Instruct',       SAMBANOVA_KEYS),
        ('nvidia',     'meta/llama-3.1-8b-instruct',       NVIDIA_KEYS),
    ],
    'deepseek-r1': [
        ('groq',       'deepseek-r1-distill-llama-70b',    GROQ_KEYS),
        ('llm7',       'deepseek-r1-0528',                LLM7_KEYS),
        ('deepseek',   'deepseek-reasoner',                DEEPSEEK_KEYS),
    ],
    'gemma-2-9b': [
        ('sambanova',  'gemma-3-12b-it',                   SAMBANOVA_KEYS),
        ('nvidia',     'google/gemma-3-27b-it',            NVIDIA_KEYS),
    ],
    'mixtral-8x7b': [
        ('groq',       'mixtral-8x7b-32768',                   GROQ_KEYS),
        ('nvidia',     'mistralai/mixtral-8x7b-instruct-v0.1',  NVIDIA_KEYS),
    ],
    'llama-3.3-70b': [
        ('groq',       'llama-3.3-70b-versatile',          GROQ_KEYS),
        ('cerebras',  'llama-3.3-70b',                     CEREBRAS_KEYS),
        ('sambanova',  'Meta-Llama-3.3-70B-Instruct',      SAMBANOVA_KEYS),
        ('nvidia',     'meta/llama-3.3-70b-instruct',      NVIDIA_KEYS),
    ]
}

def call_api(sys_p, user_p, model_name, temp=0.7, max_tok=600):
    # Check cache first
    cached_val = cache.get(sys_p, user_p, model_name)
    if cached_val is not None:
        return cached_val

    routes = PROVIDER_ROUTING.get(model_name, [])
    if not routes:
        routes = [('groq', model_name, GROQ_KEYS)]

    for prov, model_id, keys in routes:
        if not keys:
            continue
        
        num_keys = len(keys)
        start_idx = _key_indices[prov]
        
        for k_attempt in range(num_keys):
            idx = (start_idx + k_attempt) % num_keys
            key = keys[idx]
            
            try:
                if prov == 'cerebras':
                    res = call_cerebras(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'sambanova':
                    res = call_sambanova(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'nvidia':
                    res = call_nvidia(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'llm7':
                    res = call_llm7(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'deepinfra':
                    res = call_deepinfra(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'deepseek':
                    res = call_deepseek(key, model_id, sys_p, user_p, max_tok, temp)
                elif prov == 'groq':
                    res = call_groq_api(key, model_id, sys_p, user_p, max_tok, temp)
                else:
                    continue
                
                _key_indices[prov] = (idx + 1) % num_keys
                
                if res and res.strip():
                    cache.set(sys_p, user_p, model_name, res)
                    return res
            except Exception as e:
                err_str = str(e).lower()
                print(f"  [API Error] Provider: {prov}, Model: {model_id}, Key index: {idx}: {err_str[:120]}")
                _key_indices[prov] = (idx + 1) % num_keys
                if '429' in err_str or 'rate' in err_str:
                    time.sleep(2.0)

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

def validate_options_length(options, threshold=0.15):
    """Ensure all distractors are within threshold of correct option length."""
    if not options or len(options) < 4:
        return False
    len0 = len(options[0])
    if len0 == 0:
        return False
    for opt in options[1:4]:
        if abs(len(opt) - len0) / len0 > threshold:
            return False
    return True

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
                
                options = None
                for attempt in range(3):
                    raw = call_api(sys_p, user_p, model_name=args.gen_model)
                    options = parse_response_strat2(raw)
                    if options and len(options) >= 4:
                        if validate_options_length(options, threshold=0.15):
                            break
                        else:
                            print(f'  [LENGTH VALIDATION FAILED] Attempt {attempt+1}: Option lengths: {[len(x) for x in options]}')
                            user_p += f"\nRETRY WARNING: The previous options failed character-length validation. Option lengths were: {[len(x) for x in options]}. Ensure Options 2, 3, and 4 are of EXACTLY the same length as Option 1."
                    time.sleep(1.0)
                
                if not options or len(options) < 4:
                    print(f'  [PARSE/GEN FAIL] fallback to negative sampling for {row.get("sample_id","?")}')
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
            pred_raw = call_api(audit_sys, user_aud, model_name=model, temp=0.0, max_tok=5)
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
