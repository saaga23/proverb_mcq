"""
pilot_v2.py — ProverbGap Shortcut Audit Fix: Pilot Script
===========================================================
Generates 50 items per language using v2 prompts, then runs
the blind shortcut audit immediately. Prints pass/fail per language.

Usage:
  python pilot_v2.py --groq-key gsk_... --task b --n 50 --data-dir "_unzipped"

Requirements:
  pip install groq pandas

Target: blind audit accuracy < 40% for all languages (was 66-93%)
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
parser = argparse.ArgumentParser(description='ProverbGap v2 prompt pilot')
parser.add_argument('--groq-key',  default=os.environ.get('GROQ_API_KEY',''),
                    help='Groq API key (or set GROQ_API_KEY env var)')
parser.add_argument('--task',      default='b', choices=['a','b'],
                    help='a=literal, b=cultural (default: b)')
parser.add_argument('--n',         default=50, type=int,
                    help='Items per language (default: 50)')
parser.add_argument('--data-dir',  default='_unzipped',
                    help='Folder with existing mcq_*.csv files (default: _unzipped)')
parser.add_argument('--out',       default='pilot_v2_results',
                    help='Output folder (default: pilot_v2_results)')
parser.add_argument('--gen-model', default='llama-3.3-70b-versatile',
                    help='Model for generation')
parser.add_argument('--eval-model',default='llama-3.1-8b-instant',
                    help='Model for blind audit')
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

LANGUAGES = ['Yoruba', 'Arabic', 'English', 'French', 'Spanish', 'German']

print(f'\n{"="*60}')
print(f'  ProverbGap v2 Prompt Pilot')
print(f'  Task: {"B (Cultural)" if args.task=="b" else "A (Literal)"}')
print(f'  Items per language: {args.n}')
print(f'  Data dir: {DATA}')
print(f'  Gen model: {args.gen_model}')
print(f'  Eval model: {args.eval_model}')
print(f'{"="*60}\n')

# ── v2 Prompts ────────────────────────────────────────────────────────────────

# TASK B — Cultural meaning distractor generation
SYS_B_V2 = (
    'You are building a rigorous benchmark to test cultural understanding of proverbs. '
    'Given a proverb and its correct cultural meaning, generate 3 ALTERNATIVE cultural '
    'interpretations. The alternatives must:\n'
    '1. Be written in the SAME cultural register as the correct meaning — '
    'not more academic, not more casual, not more abstract\n'
    '2. Be SIMILAR in length to the correct meaning\n'
    '3. Express a DIFFERENT life lesson, social value, or communal principle '
    'than the correct meaning\n'
    '4. Sound equally plausible as genuine cultural wisdom — '
    'a reader who does not know this proverb should find all 4 options credible\n'
    '5. Be wrong because they convey a different cultural message, '
    'NOT because they sound absurd, obviously off-topic, or literal\n'
    'The 3 alternatives should be indistinguishable in format and tone from the '
    'correct meaning. Return ONLY a valid JSON list of 3 strings. No markdown.'
)

def make_prompt_b(proverb, translation, cultural_meaning, lang):
    yoruba_note = ''
    if lang == 'Yoruba':
        yoruba_note = (
            '\nIMPORTANT: Each alternative must reflect a specific Yoruba social value '
            'or communal principle — not a generic life lesson. Ground each alternative '
            'in Yoruba community life, family structure, or social hierarchy.'
        )
    return (
        f'Proverb ({lang}): {proverb}\n'
        f'English translation: {translation}\n'
        f'Correct cultural meaning: {cultural_meaning}'
        f'{yoruba_note}\n\n'
        'Generate 3 alternative cultural interpretations where each:\n'
        '- Is written in the same style and cultural register as the correct meaning above\n'
        '- Is similar in length to the correct meaning above\n'
        '- Conveys a DIFFERENT life lesson or social value\n'
        '- Sounds equally legitimate as genuine cultural wisdom\n'
        '- Is wrong because it misattributes the cultural message — not because it sounds absurd\n\n'
        'Return ONLY: ["alternative 1", "alternative 2", "alternative 3"]'
    )

# TASK A — Literal translation distractor generation
SYS_A_V2 = (
    'You are building a rigorous benchmark to test literal comprehension of proverbs. '
    'Given a proverb and its correct English translation, generate 3 ALTERNATIVE English '
    'translations. The alternatives must:\n'
    '1. Be written in the SAME natural translation register as the correct translation\n'
    '2. Be SIMILAR in length to the correct translation\n'
    '3. Introduce a SUBTLE meaning shift — different agent, direction, object, or condition '
    'compared to the correct translation\n'
    '4. Sound like genuine direct translations of a proverb\n'
    '5. Be grammatically natural English — not broken or obviously wrong\n'
    'Return ONLY a valid JSON list of 3 strings. No markdown.'
)

def make_prompt_a(proverb, translation, lang):
    return (
        f'Proverb ({lang}): {proverb}\n'
        f'Correct English translation: {translation}\n\n'
        'Generate 3 alternative translations where each:\n'
        '- Is written in the same natural translation style as the correct translation above\n'
        '- Is similar in length to the correct translation above\n'
        '- Introduces a subtle meaning difference (different agent, action, direction, or scope)\n'
        '- Sounds like a genuine direct translation of a proverb\n'
        '- Is grammatically natural English\n\n'
        'Return ONLY: ["alternative 1", "alternative 2", "alternative 3"]'
    )

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_response(raw):
    """Parse LLM output into a list of 3 distractor strings."""
    if not raw:
        return None
    # Strip reasoning tags
    raw = re.sub(r'<reasoning>.*?</reasoning>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    raw = raw.strip()
    # Strip code fences
    raw = re.sub(r'^```\w*\n?', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\n?```$', '', raw, flags=re.MULTILINE)
    raw = raw.strip()
    if not raw:
        return None
    # Strategy 1: direct JSON parse
    try:
        d = json.loads(raw)
        if isinstance(d, list) and len(d) >= 3:
            return [str(x).strip() for x in d[:3] if str(x).strip()]
    except json.JSONDecodeError:
        pass
    # Strategy 2: find embedded JSON array
    m = re.search(r'\[[\s\S]*?\]', raw)
    if m:
        try:
            d = json.loads(m.group())
            if isinstance(d, list) and len(d) >= 3:
                return [str(x).strip() for x in d[:3] if str(x).strip()]
        except json.JSONDecodeError:
            pass
    # Strategy 3: quoted strings
    matches = re.findall(r'"([^"]{8,400})"', raw)
    if len(matches) >= 3:
        return matches[:3]
    return None


def call_groq(sys_prompt, user_prompt, model, temperature=0.85, max_tokens=800):
    """Call Groq with retry."""
    for attempt in range(3):
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
            print(f'  [API err attempt {attempt+1}]: {err[:80]}')
            if 'rate_limit' in err.lower() or '429' in err:
                time.sleep(60)
            else:
                time.sleep(3)
    return None


def assemble_mcq(correct, distractors):
    """Shuffle correct + 3 distractors into A/B/C/D choices."""
    rng = random.Random(42)
    choices = list(distractors[:3]) + [correct]
    rng.shuffle(choices)
    labels = ['A', 'B', 'C', 'D']
    answer = labels[choices.index(correct)]
    choice_dict = {f'Choice_{l}': choices[i] for i, l in enumerate(labels)}
    return choice_dict, answer


# ── PHASE 1: Generation ───────────────────────────────────────────────────────

sys_p = SYS_B_V2 if args.task == 'b' else SYS_A_V2
gen_rows = []
generation_failures = {}

for lang in LANGUAGES:
    # Find source CSV
    csv_path = DATA / f'mcq_{args.task}_zs_{lang.lower()}.csv'
    if not csv_path.exists():
        print(f'[SKIP] {lang}: {csv_path} not found')
        continue

    try:
        src_df = pd.read_csv(csv_path)
    except Exception as e:
        print(f'[SKIP] {lang}: read error — {e}')
        continue

    # Drop rows with missing key fields
    required = ['source_proverb', 'proverb_en', 'correct_meaning']
    src_df = src_df.dropna(subset=required).reset_index(drop=True)

    n = min(args.n, len(src_df))
    sample = src_df.sample(n, random_state=42)

    print(f'\n[{lang}] Generating {n} items with v2 prompts...')
    fail_count = 0

    for idx, (_, row) in enumerate(sample.iterrows()):
        proverb     = str(row['source_proverb'])
        translation = str(row['proverb_en'])
        correct     = str(row['correct_meaning'])

        if args.task == 'b':
            user_p = make_prompt_b(proverb, translation, correct, lang)
        else:
            user_p = make_prompt_a(proverb, translation, lang)

        raw   = call_groq(sys_p, user_p, model=args.gen_model)
        dists = parse_response(raw)

        if not dists:
            fail_count += 1
            print(f'  [PARSE FAIL] {row.get("sample_id","?")}')
            continue

        choices, answer = assemble_mcq(correct, dists)
        gen_rows.append({
            'task':          args.task,
            'language':      lang,
            'sample_id':     str(row.get('sample_id', f'{lang[:3]}{idx:04d}')),
            'source_proverb': proverb,
            'proverb_en':    translation,
            'correct_meaning': correct,
            **choices,
            'Answer':        answer,
            'distractor_1':  dists[0],
            'distractor_2':  dists[1],
            'distractor_3':  dists[2],
        })

        if (idx + 1) % 10 == 0:
            print(f'  {idx+1}/{n} done')

        time.sleep(1.1)  # stay under Groq rate limit

    generation_failures[lang] = fail_count
    print(f'  {lang}: {n - fail_count}/{n} generated ({fail_count} parse failures)')

if not gen_rows:
    print('\nERROR: No items generated. Check data-dir and API key.')
    sys.exit(1)

gen_df = pd.DataFrame(gen_rows)
gen_path = OUT / f'pilot_v2_gen_{args.task}.csv'
gen_df.to_csv(gen_path, index=False)
print(f'\n✅ Generated {len(gen_df)} items → {gen_path}')

# ── PHASE 2: Blind Audit ──────────────────────────────────────────────────────

print(f'\n{"="*60}')
print('  BLIND AUDIT')
print('  Evaluator sees proverb + 4 choices. NO correct answer shown.')
print(f'{"="*60}')

AUDIT_SYS = (
    'You are answering a multiple-choice question about a proverb. '
    'Select the option that best matches the question. '
    'Reply with ONLY the letter: A, B, C, or D.'
)
AUDIT_Q = {
    'a': 'What does this proverb most likely mean literally?',
    'b': 'Which option best captures the cultural meaning of this proverb?',
}

def build_audit_prompt(task, proverb, translation, ca, cb, cc, cd):
    return (
        f'Proverb: {proverb}\n'
        f'English: {translation}\n\n'
        f'{AUDIT_Q[task]}\n'
        f'A. {ca}\nB. {cb}\nC. {cc}\nD. {cd}\n\n'
        'Answer (A/B/C/D only):'
    )

def parse_audit_answer(raw):
    if not raw:
        return None
    raw = raw.strip().upper()
    for ch in 'ABCD':
        if raw.startswith(ch):
            return ch
    m = re.search(r'\b([ABCD])\b', raw)
    return m.group(1) if m else None


audit_rows = []
total = len(gen_df)

print(f'\nAuditing {total} items...')
for i, (_, row) in enumerate(gen_df.iterrows()):
    ap = build_audit_prompt(
        args.task,
        row['source_proverb'], row['proverb_en'],
        row['Choice_A'], row['Choice_B'], row['Choice_C'], row['Choice_D'],
    )
    raw  = call_groq(AUDIT_SYS, ap, model=args.eval_model, temperature=0.0, max_tokens=5)
    pred = parse_audit_answer(raw)

    audit_rows.append({
        'language':   row['language'],
        'sample_id':  row['sample_id'],
        'correct':    row['Answer'],
        'predicted':  pred,
        'is_correct': int(pred == row['Answer']) if pred else 0,
    })

    if (i + 1) % 20 == 0:
        print(f'  Audited {i+1}/{total}...')

    time.sleep(0.15)

audit_df = pd.DataFrame(audit_rows)
audit_path = OUT / f'pilot_v2_audit_{args.task}.csv'
audit_df.to_csv(audit_path, index=False)

# ── PHASE 3: Report ───────────────────────────────────────────────────────────

print(f'\n{"="*60}')
print('  SHORTCUT AUDIT RESULTS — v2 Prompts')
print(f'{"="*60}')
print(f'  {"Language":<12} {"N":>5} {"Acc%":>8}  {"vs 25%":>8}  {"Status"}')
print(f'  {"-"*50}')

all_pass = True
for lang in LANGUAGES:
    sub = audit_df[audit_df['language'] == lang]
    if len(sub) == 0:
        continue
    acc   = round(sub['is_correct'].mean() * 100, 1)
    delta = acc - 25.0
    if acc < 40:
        status = '✅ PASS'
    elif acc < 55:
        status = '🟡 REVIEW'
        all_pass = False
    else:
        status = '🔴 FAIL'
        all_pass = False
    print(f'  {lang:<12} {len(sub):>5} {acc:>7.1f}%  {delta:>+7.1f}pp  {status}')

overall_acc = round(audit_df['is_correct'].mean() * 100, 1)
print(f'  {"-"*50}')
print(f'  {"OVERALL":<12} {len(audit_df):>5} {overall_acc:>7.1f}%')

print(f'\n  Target: < 40% for all languages')
print(f'  Baseline (random chance): 25%')
print(f'\n  {"✅ PROMPTS PASS — ready to scale to 1000 items!" if all_pass else "🔴 PROMPTS NEED MORE WORK — review failures above"}')

print(f'\n  Results saved to:')
print(f'    {gen_path}')
print(f'    {audit_path}')
print(f'{"="*60}\n')
