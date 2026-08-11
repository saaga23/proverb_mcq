"""
OpenRouter Pilot 2 v3 — Fresh S1/S2 MCQ generation + dynamic-pool committee audit.

This is a hardened rebuild of the Pilot 2 evaluator that borrows the infrastructure
from `openrouter_pilot_distractor_generation_test_nano_opus.py`:

* Same data source and CSV column renaming as the generation pilot.
* Dynamic, disjoint generator and audit model pools with football-style substitutions.
* Live OpenRouter catalog filtering and cheap echo preflight probes.
* Hardened `openrouter_chat` client with 400/422 fallbacks and reasoning-family
  token-limit handling.
* CostTracker with live price refresh and a $5 hard cap.
* Battle-tested parsers (`parse_options`, `extract_choice`) plus a parser self-test.
* Fresh S1 (proverb → 4 English meanings) and S2 (meaning → 4 source proverbs)
  generation with meta-text rejection, length parity, duplicate rejection, and
  corpus-based fallbacks.
* Optional sentence-transformer semantic paraphrase guard for S1 distractors.

Outputs (in /kaggle/working/ or local openrouter_pilot2_output/):
    mcqs_s1.csv
    mcqs_s2.csv
    pilot2_eval_results.csv
    pilot2_summary.json
    pilot2_state.json
    pilot2_raw_outputs.csv
"""

import os
import re
import json
import time
import random
import hashlib
import requests
import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime, timezone

# ── Configuration ───────────────────────────────────────────────────────────

SEED = 20260615
N_PER_LANG = 10                       # per-language sample; lower for a smoke test
COST_CAP_USD = 5.0
TEMPERATURE = 0.0

MAX_TOKENS_GEN = 4096                 # high ceiling; falls back if provider rejects it
MAX_TOKENS_AUDIT = 256

# Length parity ±20% against the median length of all four options.
LENGTH_CHECK_THRESHOLD = 0.20

# Semantic paraphrase guard: S1 distractors with cosine similarity above this
# threshold to the correct meaning are treated as near-paraphrases and replaced.
SEMANTIC_SIM_THRESHOLD = 0.85

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"

MIN_ACTIVE_GENERATORS = 1
MIN_ACTIVE_COMMITTEE = 2

# Generator pool: one active generator is used for both S1 and S2 generation.
# Starters are the first GENERATOR_STARTERS entries; the rest are substitutes.
# anthropic/claude-opus-4.8 was dropped because it is too expensive for the
# scale of data we plan to evaluate; anthropic/claude-sonnet-4 is the cheaper
# Anthropic stand-in and is available as a starter fallback.
GENERATOR_POOL = [
    # Starters
    "google/gemini-2.5-pro",
    "qwen/qwen3.5-397b-a17b",
    "anthropic/claude-sonnet-4",
    # Substitutes
    "google/gemma-4-31b-it",
    "deepseek/deepseek-v4-pro",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1-nano",
]
GENERATOR_STARTERS = 3

# Audit committee — deliberately disjoint from the generator pool.
AUDIT_POOL = [
    # Starters
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct",
    "google/gemma-3-27b-it",
    "deepseek/deepseek-v3.2",  # promoted from substitute; claude-3.5-haiku is EOL
    # Substitutes
    "amazon/nova-lite-v1",
]
AUDIT_STARTERS = 4

# OpenRouter pass-through pricing (USD per 1M tokens) as of 2026-06-19.
PRICE_TABLE = {
    "anthropic/claude-opus-4.8": {"input": 5.0, "output": 25.0},
    "anthropic/claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "openai/gpt-5": {"input": 1.25, "output": 10.0},
    "openai/gpt-4.1": {"input": 2.0, "output": 8.0},
    "openai/gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "openai/gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "qwen/qwen3.5-397b-a17b": {"input": 0.39, "output": 0.90},
    "qwen/qwen3.7-max": {"input": 1.25, "output": 3.75},
    "qwen/qwen3-14b": {"input": 0.05, "output": 0.15},
    "qwen/qwen3-32b": {"input": 0.08, "output": 0.28},
    "google/gemma-4-31b-it": {"input": 0.12, "output": 0.36},
    "google/gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "google/gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "google/gemini-2.5-flash-preview": {"input": 0.15, "output": 0.60},
    "google/gemma-3-27b-it": {"input": 0.08, "output": 0.16},
    "meta-llama/llama-4-maverick": {"input": 0.15, "output": 0.60},
    "meta-llama/llama-4-scout-17b-16e-instruct": {"input": 0.10, "output": 0.30},
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.10, "output": 0.32},
    "meta-llama/llama-3.1-405b-instruct": {"input": 2.8, "output": 2.8},
    "deepseek/deepseek-v4-pro": {"input": 0.435, "output": 0.87},
    "deepseek/deepseek-v3.2": {"input": 0.2288, "output": 0.3432},
    "mistralai/mistral-small-3.2-24b-instruct": {"input": 0.075, "output": 0.20},
    "amazon/nova-lite-v1": {"input": 0.06, "output": 0.24},
}
DEFAULT_PRICE = {"input": 2.0, "output": 8.0}

# Paths
DATA_DIR = "/kaggle/input/datasets/abrahamsunday123/full-data-complete"
OUTPUT_DIR = "/kaggle/working/"
if not os.path.exists(DATA_DIR):
    DATA_DIR = "actual_data/cleaned"
    OUTPUT_DIR = "openrouter_pilot2_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)
STATE_PATH = os.path.join(OUTPUT_DIR, "pilot2_state.json")

# Independent position counters for balanced A-D placement.
# S1 and S2 are keyed separately so that separate S1/S2 loops do not create
# position-bias artifacts (e.g., S1 keys only A/C and S2 keys only B/D).
S1_POSITION_COUNTER = 0
S2_POSITION_COUNTER = 0

# Raw-output log for forensics.
RAW_OUTPUTS = []

# Lazy-loaded sentence transformer for the S1 semantic paraphrase guard.
_SEMANTIC_MODEL = None

# ── API key ─────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = None

try:
    from kaggle_secrets import UserSecretsClient
    OPENROUTER_API_KEY = UserSecretsClient().get_secret("OPENROUTER_API_KEY")
except Exception:
    pass

if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found. Add it to Kaggle Secrets or set it as an environment variable."
    )


# ── Safe printing ───────────────────────────────────────────────────────────

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            text = " ".join(str(a) for a in args)
            print(text.encode("ascii", "ignore").decode("ascii"), **kwargs)
        except Exception:
            pass


# ── Cost tracking ───────────────────────────────────────────────────────────

class CostTracker:
    def __init__(self, cap, spent=0.0, history=None):
        self.cap = cap
        self.spent = spent
        self.history = list(history or [])

    def estimate(self, model, input_tokens, output_tokens):
        p = PRICE_TABLE.get(model, DEFAULT_PRICE)
        return (input_tokens * p["input"] + output_tokens * p["output"]) / 1e6

    def would_exceed(self, model, input_tokens, output_tokens):
        return (self.spent + self.estimate(model, input_tokens, output_tokens)) > self.cap

    def add(self, model, input_tokens, output_tokens, purpose):
        p = PRICE_TABLE.get(model, DEFAULT_PRICE)
        cost = (input_tokens * p["input"] + output_tokens * p["output"]) / 1e6
        self.spent += cost
        self.history.append({
            "model": model,
            "purpose": purpose,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "cumulative_usd": self.spent,
        })
        return cost

    def check(self):
        if self.spent >= self.cap:
            raise RuntimeError(
                f"Cost cap ${self.cap:.2f} exceeded (spent ${self.spent:.2f}). Aborting."
            )


cost_tracker = CostTracker(COST_CAP_USD)


# ── Model pool (football-style substitutions) ───────────────────────────────

class ModelPool:
    """
    Manage an ordered roster of models. The first `active_limit` models are
    starters; the remainder are substitutes. Repeated failures (weighted) bench
    a model and promote the next available substitute.
    """

    def __init__(self, pool, active_limit, name, fail_threshold=2, state=None):
        self.name = name
        self.pool = list(pool)
        self.fail_threshold = fail_threshold
        if state:
            self.active = list(state.get("active", []))
            self.benched = list(state.get("benched", []))
            self.failure_counts = dict(state.get("failure_counts", {}))
            self.substitutions = list(state.get("substitutions", []))
        else:
            self.active = list(pool[:active_limit])
            self.benched = []
            self.failure_counts = {}
            self.substitutions = []

    def record_failure(self, model, weight=1, reason=""):
        """Increment failure count for an active model and bench if threshold reached."""
        if model not in self.active:
            return None
        self.failure_counts[model] = self.failure_counts.get(model, 0) + weight
        if self.failure_counts[model] >= self.fail_threshold:
            return self.bench(model, reason=f"{reason} (fail_count={self.failure_counts[model]})")
        return None

    def reset_failure_streak(self, model):
        """Clear failures for a model after a successful call."""
        if model in self.failure_counts:
            self.failure_counts[model] = 0

    def bench(self, model, reason=""):
        """Move a model to the bench and promote the next available substitute."""
        if model in self.active:
            self.active.remove(model)
        if model not in self.benched:
            self.benched.append(model)

        substitute = None
        for m in self.pool:
            if m not in self.active and m not in self.benched:
                substitute = m
                break

        if substitute:
            self.active.append(substitute)
            self.failure_counts[substitute] = 0
            self.substitutions.append({
                "out": model,
                "in": substitute,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            safe_print(f"[POOL] {self.name} SUBSTITUTION: {model} -> {substitute} ({reason})")
        else:
            self.substitutions.append({
                "out": model,
                "in": None,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            safe_print(f"[POOL] {self.name} SUBSTITUTION: {model} -> None (no substitute; {reason})")
        return substitute

    def filter_by_catalog(self, live_models):
        """Bench any active model not present in the live OpenRouter catalog."""
        if not live_models:
            return []
        removed = []
        for model in list(self.active):
            if model not in live_models:
                removed.append(model)
                self.bench(model, reason="not_in_live_catalog")
        return removed

    def exclude(self, model, reason=""):
        """Permanently remove a model from consideration (starter or substitute)."""
        if model in self.active:
            self.bench(model, reason=reason)
        elif model not in self.benched:
            self.benched.append(model)
            self.substitutions.append({
                "out": model,
                "in": None,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            safe_print(f"[POOL] {self.name} EXCLUDED {model} ({reason})")

    def state_dict(self):
        return {
            "name": self.name,
            "pool": self.pool,
            "active": self.active,
            "benched": self.benched,
            "failure_counts": self.failure_counts,
            "substitutions": self.substitutions,
            "fail_threshold": self.fail_threshold,
        }


# Global pools; rehydrated from saved state in main() if available.
generator_pool = ModelPool(GENERATOR_POOL, GENERATOR_STARTERS, "GENERATOR")
audit_pool = ModelPool(AUDIT_POOL, AUDIT_STARTERS, "AUDIT")


# ── Live-catalog helpers ────────────────────────────────────────────────────

def refresh_price_table(model_ids):
    """Fetch live OpenRouter prices for any model not already in PRICE_TABLE."""
    try:
        r = requests.get(MODELS_URL, timeout=30)
        r.raise_for_status()
        live = {m["id"]: m.get("pricing", {}) for m in r.json().get("data", [])}
        refreshed = 0
        for mid in model_ids:
            if mid in live and mid not in PRICE_TABLE:
                p = live[mid]
                try:
                    inp = float(p.get("prompt", 0)) * 1e6
                    out = float(p.get("completion", 0)) * 1e6
                    if inp >= 0 and out >= 0:
                        PRICE_TABLE[mid] = {"input": inp, "output": out}
                        refreshed += 1
                except Exception:
                    pass
        safe_print(f"Price table refreshed: {refreshed} models added")
    except Exception as e:
        safe_print(f"WARN: could not refresh price table: {e}")


def api_preflight(model, max_tokens=None):
    """Cheap probe: ask the model to echo a single letter."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say the letter A and nothing else."},
    ]
    for attempt in range(2):
        try:
            resp = openrouter_chat(model, messages, max_tokens=max_tokens)
            text = extract_text(resp)
            if text and "A" in text.upper():
                safe_print(f"  [CHEAP PREFLIGHT OK] {model}: {text[:20]!r}")
                return True
            safe_print(f"  [CHEAP PREFLIGHT FAIL] {model}: got {text!r}")
        except Exception as e:
            safe_print(f"  [CHEAP PREFLIGHT FAIL] {model}: {e}")
    return False


# ── Data loading ────────────────────────────────────────────────────────────

def load_proverbs():
    """Load cleaned proverb corpora for all three languages."""
    paths = {
        "English": os.path.join(DATA_DIR, "English_cleaned.csv"),
        "Arabic": os.path.join(DATA_DIR, "Arabic_cleaned.csv"),
        "Yoruba": os.path.join(DATA_DIR, "Yoruba_cleaned.csv"),
    }
    records = []
    for lang, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing data file: {path}")
        df = pd.read_csv(path, encoding="utf-8")
        if lang == "English":
            df = df.rename(columns={"Proverb": "proverb", "Correct_Meaning": "meaning"})
        elif lang == "Arabic":
            df = df.rename(columns={"source_text": "proverb", "english_translation": "meaning"})
        else:
            df = df.rename(columns={"Source_Text_Yo": "proverb", "Target_Text_En": "meaning"})
        df = df[["proverb", "meaning"]].dropna()
        df["language"] = lang
        df["sample_id"] = df.index.astype(str)
        records.append(df)
    return pd.concat(records, ignore_index=True)


def sample_per_language(df, n, seed):
    rng = np.random.default_rng(seed)
    sampled = []
    for lang, group in df.groupby("language"):
        group = group.reset_index(drop=True)
        k = min(n, len(group))
        if k == len(group):
            sampled.append(group)
        else:
            idx = rng.choice(len(group), size=k, replace=False)
            sampled.append(group.iloc[idx])
    return pd.concat(sampled, ignore_index=True)


# ── OpenRouter client ───────────────────────────────────────────────────────

def openrouter_chat(model, messages, max_tokens=None, response_format=None, retries=3):
    """
    Call OpenRouter with retries and 400/422 fallbacks.
    Strategy order:
      1. payload with max_tokens (if provided) + response_format (if provided)
      2. payload without max_tokens + response_format
      3. payload with max_tokens but no response_format
      4. payload without either
    Returns the raw JSON response dict.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://www.kaggle.com/",
        "X-Title": "ProverbGap Pilot 2 v3",
    }

    def _token_limit_kwargs(model, max_tokens):
        """Use max_completion_tokens for OpenAI reasoning families."""
        if model.startswith(("openai/gpt-5", "openai/o1", "openai/o3", "openai/o4")):
            return {"max_completion_tokens": max_tokens if max_tokens is not None else 4096}
        if max_tokens is not None:
            return {"max_tokens": max_tokens}
        return {}

    def make_payload(include_max, include_format):
        p = {"model": model, "messages": messages, "temperature": TEMPERATURE}
        if include_max and max_tokens is not None:
            p.update(_token_limit_kwargs(model, max_tokens))
        if include_format and response_format is not None:
            p["response_format"] = response_format
        return p

    strategies = [
        make_payload(True, True),
        make_payload(False, True),
        make_payload(True, False),
        make_payload(False, False),
    ]
    seen = []
    for s in strategies:
        if s not in seen:
            seen.append(s)
    strategies = seen

    last_error = None
    for payload in strategies:
        for attempt in range(retries):
            try:
                r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=180)
                r.raise_for_status()
                return r.json()
            except requests.exceptions.HTTPError as e:
                last_error = e
                status = e.response.status_code if e.response else 0
                body = ""
                try:
                    body = e.response.text[:500]
                except Exception:
                    pass
                safe_print(f"  HTTP {status} for {model} (strategy {strategies.index(payload)+1}/{len(strategies)}): {body}")
                if status in (429, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                break
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                break
    raise last_error or RuntimeError(f"All strategies failed for {model}")


def extract_text(response):
    """Extract content from OpenRouter response, with refusal/reasoning fallbacks."""
    if not response or "choices" not in response or not response["choices"]:
        return ""
    msg = response["choices"][0].get("message") or {}
    text = msg.get("content") or ""
    if text:
        return text.strip()
    for key in ("reasoning", "refusal"):
        val = msg.get(key)
        if val:
            return str(val).strip()
    return ""


def extract_finish_reason(response):
    if not response or "choices" not in response or not response["choices"]:
        return None
    return response["choices"][0].get("finish_reason")


def extract_usage(response):
    usage = response.get("usage", {}) if response else {}
    return usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def response_snippet(response, length=800):
    if not response:
        return "(no response)"
    try:
        return json.dumps(response, ensure_ascii=False, indent=2)[:length]
    except Exception:
        return str(response)[:length]


# ── JSON / option parsing ───────────────────────────────────────────────────

REASONING_TAGS = re.compile(r"<think>.*?</think>|<reasoning>.*?</reasoning>", re.DOTALL | re.IGNORECASE)


def extract_balanced(text, open_char, close_char):
    """Return the first balanced bracket/brace substring, or None."""
    if not text:
        return None
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == open_char:
            if depth == 0:
                start = i
            depth += 1
        elif ch == close_char:
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i + 1]
    return None


def clean_model_output(text):
    if not text:
        return text
    text = REASONING_TAGS.sub("", text)
    # Discard any trailing "INVALID JSON" marker and everything after it.
    text = re.split(r"\*\*INVALID JSON\*\*", text, maxsplit=1)[0]
    # Prefer JSON inside a markdown code fence.
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()
    # Otherwise extract the first balanced array or object.
    for open_ch, close_ch in (("[", "]"), ("{", "}")):
        balanced = extract_balanced(text, open_ch, close_ch)
        if balanced:
            return balanced.strip()
    return text.strip()


def parse_options(text):
    """
    Parse model output into a list of exactly 4 option strings.
    Tries, in order:
      1. Cleaned JSON array of 4 strings.
      2. JSON object whose values are 4 strings (numeric keys or any keys).
      3. Regex extraction of exactly 4 quoted strings.
      4. Plain-text line splitting (numbered/bulleted lists or one-per-line).
    """
    cleaned = clean_model_output(text)

    opts = None
    for candidate in (cleaned, cleaned.strip().strip(",").strip(), cleaned.replace("'", '"')):
        try:
            opts = json.loads(candidate)
            break
        except Exception:
            continue

    if isinstance(opts, list) and len(opts) == 4 and all(isinstance(o, str) for o in opts):
        return [o.strip() for o in opts]

    if isinstance(opts, dict):
        for key in ("options", "choices", "distractors", "answers", "items", "result"):
            arr = opts.get(key)
            if isinstance(arr, list) and len(arr) == 4 and all(isinstance(o, str) for o in arr):
                return [o.strip() for o in arr]
        str_vals = [v for v in opts.values() if isinstance(v, str)]
        if len(str_vals) == 4:
            return [v.strip() for v in str_vals]
        try:
            numeric_items = [(int(k), v) for k, v in opts.items() if isinstance(v, str) and str(k).lstrip("-").isdigit()]
            if len(numeric_items) == 4:
                numeric_items.sort(key=lambda x: x[0])
                return [v.strip() for _, v in numeric_items]
        except Exception:
            pass

    quoted_strings = re.findall(r"['\"](.*?)['\"]", cleaned, re.DOTALL)
    filtered = [s for s in quoted_strings if len(s.strip()) > 5 and s.strip().lower() not in {
        "options", "choices", "distractors", "answers", "items", "result", "error"
    }]
    if len(filtered) == 4:
        return [s.strip() for s in filtered]

    lines = []
    for ln in (text or "").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        ln = re.sub(r"^(\s*[-*•]\s+|\s*\d+[.):\]]\s+|\s*\([a-dA-D]\)\s+|\s*[a-dA-D][.):\]]\s+)", "", ln)
        ln = ln.strip('"').strip("'")
        if ln:
            lines.append(ln)
    if len(lines) >= 4:
        return lines[:4]

    return None


# ── Validation utilities ────────────────────────────────────────────────────

def jaccard(a, b):
    """Token-overlap similarity; 0 = distinct, 1 = identical."""
    sa, sb = set(str(a).lower().split()), set(str(b).lower().split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _median_length(opts):
    lengths = [len(str(o)) for o in opts]
    return int(np.median(lengths)) if lengths else 0


def passes_length_check(candidate, reference, threshold=LENGTH_CHECK_THRESHOLD):
    """Character-count parity against a reference length (or median of a list)."""
    if isinstance(reference, (list, tuple)):
        ref_len = _median_length(reference)
    else:
        ref_len = len(str(reference))
    cand_len = len(str(candidate))
    if ref_len > 0 and abs(cand_len - ref_len) / ref_len <= threshold:
        return True, "length"
    return False, f"length_ratio={cand_len / max(ref_len, 1):.2f}"


def has_meta_words(text):
    meta = {"incorrect", "wrong", "not", "opposite", "false", "untrue", "invalid", "distractor", "option"}
    tokens = set(str(text).lower().split())
    return bool(tokens & meta)


# Forbidden surface patterns that models sometimes emit instead of real options.
_META_PATTERNS = [
    # Markdown formatting (bold, italic, underline, inline code)
    re.compile(r"\*\*.*?\*\*", re.DOTALL),
    re.compile(r"(?<!\*)\*(?!\*)[^*]+\*(?!\*)"),   # single *emphasis* not touching **
    re.compile(r"__.*?__"),
    re.compile(r"_.*?_"),
    re.compile(r"`[^`]*`"),
    # Headings (Markdown, pseudo-headings, and instruction leaks)
    re.compile(r"^#+\s+", re.MULTILINE),
    re.compile(r"\b(crafting|generating|creating|writing|producing|designing|building|formulating)\s+(options|distractors|answers|choices|items)\b", re.IGNORECASE),
    re.compile(r"\b(options?|distractors?|answers?|choices?|items?)\s*[\-\:]\s*", re.IGNORECASE),
    # JSON / meta phrases
    re.compile(r"\b(invalid json|json array|valid json|here is|below are|above are|the following)\b", re.IGNORECASE),
    # Explicit heading / stage labels models emit
    re.compile(r"\b(step\s*\d+|final output|selected options|candidate options|correct answer|incorrect options)\b", re.IGNORECASE),
]


def option_has_meta_text(text):
    """Return True if a single option string contains markdown/heading/instruction leaks."""
    text = str(text).strip()
    if not text:
        return True
    for pat in _META_PATTERNS:
        if pat.search(text):
            return True
    return False


def has_meta_text(opts):
    """Return True if any option in a full 4-option list contains markdown, headings, or instructions."""
    if not opts or len(opts) != 4:
        return True
    for o in opts:
        if option_has_meta_text(o):
            return True
    return False


# Generic English idioms that should never appear as options for Yoruba proverbs.
_YORUBA_ENGLISH_IDIOM_BLOCKLIST = [
    "a bird in the hand is worth two in the bush",
    "a bird in hand is worth two in the bush",
    "the apple does not fall far from the tree",
    "in unity there is strength",
    "kindness begets kindness",
    "to take the credit for someone else's work",
    "a friend in need is a friend indeed",
    "actions speak louder than words",
    "all that glitters is not gold",
    "better late than never",
    "don't count your chickens before they hatch",
    "do not count your chickens before they hatch",
    "every cloud has a silver lining",
    "the early bird catches the worm",
    "honesty is the best policy",
    "practice makes perfect",
    "when the going gets tough, the tough get going",
    "you can't have your cake and eat it too",
    "you cannot have your cake and eat it too",
    "a hungry stomach has no ears",
    "do not eat your bread on somebody else's table",
    "lost is the person who forgets his past",
    "wrong and strong",
    "the buck stops here",
    "no one is so powerful that they can stop the march of time",
    "rome was not built in a day",
    "every dog has its day",
    "where there is a will there is a way",
    "two wrongs do not make a right",
    "two wrongs don't make a right",
    "a rolling stone gathers no moss",
    "do not put all your eggs in one basket",
    "don't put all your eggs in one basket",
    "the grass is always greener on the other side",
    "you reap what you sow",
    "a penny saved is a penny earned",
    "curiosity killed the cat",
    "do not judge a book by its cover",
    "don't judge a book by its cover",
    "blood is thicker than water",
    "charity begins at home",
    "cleanliness is next to godliness",
    "easy come easy go",
    "every rose has its thorn",
    "good things come to those who wait",
    "if it ain't broke don't fix it",
    "it is not over until the fat lady sings",
    "kill two birds with one stone",
    "laughter is the best medicine",
    "let sleeping dogs lie",
    "look before you leap",
    "money does not grow on trees",
    "necessity is the mother of invention",
    "once bitten twice shy",
    "out of sight out of mind",
    "the pen is mightier than the sword",
    "there is no place like home",
    "time heals all wounds",
    "too many cooks spoil the broth",
    "when in rome do as the romans do",
    "you cannot have your cake and eat it too",
    "a chain is only as strong as its weakest link",
    "a fool and his money are soon parted",
    "a leopard cannot change its spots",
    "a little learning is a dangerous thing",
    "a picture is worth a thousand words",
    "a watched pot never boils",
    "all good things must come to an end",
    "an apple a day keeps the doctor away",
    "ask no questions and hear no lies",
    "beauty is in the eye of the beholder",
    "beggars can't be choosers",
    "better safe than sorry",
    "birds of a feather flock together",
    "clothes do not make the man",
    "curiosity killed the cat satisfaction brought it back",
    "do not bite the hand that feeds you",
    "do not cry over spilled milk",
    "do not make a mountain out of a molehill",
    "do not put the cart before the horse",
    "do not throw the baby out with the bathwater",
    "every dog has his day",
    "familiarity breeds contempt",
    "fortune favors the bold",
    "great minds think alike",
    "he who hesitates is lost",
    "honesty is the best policy",
    "hope for the best but prepare for the worst",
    "ignorance is bliss",
    "it takes two to tango",
    "keep your friends close and your enemies closer",
    "knowledge is power",
    "leave no stone unturned",
    "lightning never strikes twice in the same place",
    "like father like son",
    "make hay while the sun shines",
    "money talks",
    "no man is an island",
    "nothing ventured nothing gained",
    "once bitten twice shy",
    "one man's trash is another man's treasure",
    "people who live in glass houses should not throw stones",
    "practice what you preach",
    "the proof of the pudding is in the eating",
    "the road to hell is paved with good intentions",
    "the squeaky wheel gets the grease",
    "there is no such thing as a free lunch",
    "time is money",
    "two heads are better than one",
    "walk the walk",
    "what does not kill you makes you stronger",
    "when the cat's away the mice will play",
    "where there is smoke there is fire",
    "you can lead a horse to water but you cannot make it drink",
    "you cannot have your cake and eat it too",
    "you cannot teach an old dog new tricks",
]


def _normalize_for_blocklist(text):
    """Normalize option text for fuzzy blocklist matching."""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_yoruba_english_idiom(opts):
    """Return True if any option is a generic English idiom/proverb (Yoruba only)."""
    if not opts:
        return False
    for o in opts:
        text = _normalize_for_blocklist(o)
        for blocked in _YORUBA_ENGLISH_IDIOM_BLOCKLIST:
            if _normalize_for_blocklist(blocked) in text:
                return True
    return False


# ── Semantic paraphrase guard (optional) ────────────────────────────────────

def _load_semantic_model():
    global _SEMANTIC_MODEL
    if _SEMANTIC_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _SEMANTIC_MODEL = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            safe_print("Loaded sentence-transformer semantic paraphrase guard.")
        except Exception as e:
            safe_print(f"WARN: sentence-transformers not available; falling back to token overlap for paraphrase guard: {e}")
            _SEMANTIC_MODEL = False
    return _SEMANTIC_MODEL


def semantic_similarities(reference, candidates):
    """Return a similarity score between reference and each candidate.

    Uses cosine similarity of sentence embeddings when available, otherwise
    falls back to Jaccard token overlap.  Higher = more similar.
    """
    model = _load_semantic_model()
    if not model:
        return [jaccard(reference, c) for c in candidates]

    try:
        ref_vec = model.encode(str(reference), convert_to_numpy=True)
        cand_vecs = model.encode([str(c) for c in candidates], convert_to_numpy=True)
        ref_norm = np.linalg.norm(ref_vec)
        cand_norms = np.linalg.norm(cand_vecs, axis=1)
        if ref_norm == 0:
            return [0.0] * len(candidates)
        sims = np.dot(cand_vecs, ref_vec) / (cand_norms * ref_norm)
        return np.nan_to_num(sims).tolist()
    except Exception as e:
        safe_print(f"WARN: semantic similarity computation failed: {e}; using Jaccard fallback.")
        return [jaccard(reference, c) for c in candidates]


# ── Corpus-based fallback samplers ──────────────────────────────────────────

def semantically_distinct_negative_sample(reference_meaning, all_meanings, rng, n=1,
                                          max_jaccard=0.5, language=None, df_all=None):
    """Return n fallback distractor meanings from the corpus."""
    def build_pool(candidates):
        pool = [m for m in candidates if m != reference_meaning and jaccard(reference_meaning, m) <= max_jaccard]
        rng.shuffle(pool)
        return pool

    candidates = []
    if df_all is not None and language is not None:
        same_lang = df_all[df_all["language"] == language]["meaning"].tolist()
        candidates = build_pool(same_lang)
    if len(candidates) < n:
        candidates = build_pool(list(all_meanings))

    selected = []
    for m in candidates:
        if m not in selected and all(jaccard(m, s) <= max_jaccard for s in selected + [reference_meaning]):
            selected.append(m)
        if len(selected) == n:
            return selected
    # If the corpus is too sparse, relax distinctness but avoid duplicates.
    for m in candidates:
        if m not in selected:
            selected.append(m)
        if len(selected) == n:
            return selected
    while len(selected) < n:
        selected.append(reference_meaning + " (fallback)")
    return selected[:n]


def proverb_negative_sample(reference_proverb, language, df_all, rng, n=3):
    """Sample n proverbs from the same language, excluding the reference proverb."""
    others = df_all[(df_all["language"] == language) & (df_all["proverb"] != reference_proverb)]["proverb"].tolist()
    if len(others) < n:
        others = others * (n // max(len(others), 1) + 1)
    rng.shuffle(others)
    return others[:n]


def _log_raw(stage, model, strategy, language, proverb, meaning, raw_text, finish_reason,
             status, error=None, extracted=None):
    rec = {
        "stage": stage,
        "model": model,
        "strategy": strategy,
        "language": language,
        "proverb": proverb,
        "meaning": meaning,
        "raw_model_output": raw_text or "",
        "finish_reason": finish_reason,
        "status": status,
    }
    if error is not None:
        rec["error"] = error
    if extracted is not None:
        rec["extracted"] = extracted
    RAW_OUTPUTS.append(rec)


# ── S1 generation (proverb → 4 English meanings) ────────────────────────────

S1_SYSTEM_PROMPT = (
    "You are a JSON API for proverb multiple-choice generation. "
    "You MUST respond with ONLY a valid JSON array of exactly 4 strings. "
    "No markdown, no explanations, no code fences, no thinking tags, no extra text."
)

S1_USER_TEMPLATE = """Proverb ({language}): {proverb}
Correct meaning: {correct_meaning}

Generate 4 English answer options as a JSON array of strings:
- Index 0: a natural paraphrase of the correct meaning above.
- Index 1-3: plausible wrong meanings that a fluent speaker might choose if they had not heard this exact proverb.

Anti-contamination / quality rules:
1. Output ONLY the JSON array; do not explain your reasoning.
2. All four options must be similar in length (within ~20% character count of each other) and share the same register.
3. Do NOT use meta-words such as 'incorrect', 'wrong', 'not', 'opposite', 'false', 'untrue', 'invalid', 'distractor', or 'option'.
4. Do NOT include any source-language words or transliterations.
5. Each distractor must express a proposition that is clearly false for this proverb, not a near-paraphrase of the correct meaning.
6. Distractors should vary in the type of error they make (e.g., wrong scope, wrong cause, overgeneralization, opposite lesson) rather than following a fixed template.

Return ONLY: ["...", "...", "...", "..."]"""


def _make_s1_fallback(correct_meaning, all_meanings, rng, language, df_all):
    """Return a 4-option list when a generator call fails."""
    distractors = semantically_distinct_negative_sample(
        correct_meaning, all_meanings, rng, n=3, language=language, df_all=df_all
    )
    return [correct_meaning] + distractors


def generate_s1_mcq(proverb, meaning, language, rng, all_meanings, df_all, generator_model):
    """Generate an S1 MCQ from a proverb.

    Returns (options, meta).  options[0] is the correct meaning.
    """
    cost_tracker.check()
    prompt_tokens_est = len(S1_USER_TEMPLATE.split()) + len(str(proverb).split()) + len(str(meaning).split()) + 50
    output_tokens_est = 200

    # Cost-cap guard before the network call.
    if cost_tracker.would_exceed(generator_model, prompt_tokens_est, output_tokens_est):
        error = f"Call would exceed ${COST_CAP_USD:.2f} cap (spent ${cost_tracker.spent:.4f})."
        safe_print(f"  [S1 HARD_FALLBACK] {generator_model}: {error}")
        opts = _make_s1_fallback(meaning, all_meanings, rng, language, df_all)
        _log_raw("generation", generator_model, "S1", language, proverb, meaning,
                 "", None, "hard_fallback", error=error)
        return opts, {"status": "hard_fallback", "error": error, "fallback_count": 0, "failure_weight": 2}

    user_prompt = S1_USER_TEMPLATE.format(
        proverb=proverb, language=language, correct_meaning=meaning
    )
    # Yoruba-specific cultural-context reminder.
    if language and language.lower() == "yoruba":
        user_prompt += (
            "\n\nImportant cultural-context instruction: This is a Yoruba proverb. "
            "The four options must reflect Yoruba worldview and cultural logic. "
            "Do NOT use generic English idioms or proverbs (e.g., 'a bird in the hand', "
            "'the apple does not fall far from the tree', 'in unity there is strength') "
            "unless they are semantically tied to this specific Yoruba meaning. "
            "Distractors must be plausible misinterpretations within a Yoruba cultural frame."
        )
    messages = [
        {"role": "system", "content": S1_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    raw_text = None
    finish_reason = None
    try:
        resp = openrouter_chat(generator_model, messages, max_tokens=MAX_TOKENS_GEN, response_format=None)
        text = extract_text(resp)
        raw_text = text
        finish_reason = extract_finish_reason(resp)
        prompt_tok, out_tok = extract_usage(resp)
        cost_tracker.add(generator_model, prompt_tok or prompt_tokens_est, out_tok,
                         f"S1-gen-{generator_model}-{language}")

        if not text or not text.strip():
            raise ValueError("Empty response content")
        if finish_reason == "length":
            raise ValueError("Truncated response (finish_reason=length)")

        opts = parse_options(text)
        if opts is None:
            raise ValueError(f"Could not parse S1 options. finish_reason={finish_reason}")
        if has_meta_text(opts):
            raise ValueError(f"Parsed S1 options contain meta-text / markdown: {opts!r}")
        if language and language.lower() == "yoruba" and has_yoruba_english_idiom(opts):
            raise ValueError(f"Yoruba S1 options contain a generic English idiom: {opts!r}")
    except Exception as e:
        is_hard = (finish_reason == "length" or raw_text is None or not str(raw_text).strip())
        weight = 2 if is_hard else 1
        status = "hard_fallback" if is_hard else "parse_fallback"
        safe_print(f"  [S1 {status.upper()}] {generator_model}: {e}")
        opts = _make_s1_fallback(meaning, all_meanings, rng, language, df_all)
        _log_raw("generation", generator_model, "S1", language, proverb, meaning,
                 raw_text, finish_reason, status, error=str(e))
        return opts, {"status": status, "error": str(e), "fallback_count": 0, "failure_weight": weight}

    # Fix the correct option if the model did not put it at index 0.
    # We trust the prompt, but prefer the gold meaning at index 0 for downstream assembly.
    opts[0] = str(meaning).strip()

    # Validate distractors: no meta-words, length parity, semantic distinctness, duplicates.
    validated = [opts[0]]
    fallback_count = 0
    seen = {opts[0].strip().lower()}

    distractor_texts = opts[1:]
    sims = semantic_similarities(opts[0], distractor_texts)

    for d, sim in zip(distractor_texts, sims):
        d = str(d).strip()
        replaced = False

        if not d or has_meta_words(d):
            replaced = True
        elif option_has_meta_text(d):
            replaced = True
        elif d.strip().lower() in seen:
            replaced = True
        else:
            ok_len, _ = passes_length_check(d, opts)
            if not ok_len:
                replaced = True
            elif sim > SEMANTIC_SIM_THRESHOLD:
                replaced = True

        if replaced:
            fallback_count += 1
            alt = semantically_distinct_negative_sample(
                opts[0], all_meanings, rng, n=1, language=language, df_all=df_all
            )[0]
            d = str(alt).strip()

        validated.append(d)
        seen.add(d.strip().lower())

    status = "generated" if fallback_count == 0 else ("partial" if fallback_count < 3 else "length_fallback")
    _log_raw("generation", generator_model, "S1", language, proverb, meaning,
             raw_text, finish_reason, status)
    return validated, {"status": status, "fallback_count": fallback_count, "failure_weight": 0}


# ── S2 generation (meaning → 4 source-language proverbs) ────────────────────

S2_SYSTEM_PROMPT = (
    "You are a JSON API for proverb multiple-choice generation. "
    "You MUST respond with ONLY a valid JSON array of exactly 4 strings. "
    "No markdown, no explanations, no code fences, no thinking tags, no extra text."
)

S2_USER_TEMPLATE = """Meaning: {correct_meaning}
Correct proverb ({language}): {proverb}

Generate 4 proverb options as a JSON array of strings:
- Index 0: the correct proverb above, exactly as given.
- Index 1-3: other {language} proverbs or sayings that a fluent speaker might confuse with the meaning above.

Anti-contamination / quality rules:
1. Output ONLY the JSON array; do not explain your reasoning.
2. All four options must be real, idiomatic {language} proverbs or sayings, not made-up sentences.
3. Distractors must be genuinely different proverbs, not minor rewordings of the correct proverb.
4. Do NOT translate the distractors into English; keep them in {language}.
5. Options should be roughly similar in length and style.
6. Do NOT include meta-words such as 'incorrect', 'wrong', 'not', 'opposite', 'false', 'distractor', or 'option'.

Return ONLY: ["...", "...", "...", "..."]"""


def _make_s2_fallback(correct_proverb, language, df_all, rng):
    """Return a 4-option list when an S2 generator call fails."""
    distractors = proverb_negative_sample(correct_proverb, language, df_all, rng, n=3)
    return [correct_proverb] + distractors


def _ascii_ratio(text):
    text = str(text)
    if not text:
        return 0.0
    return sum(1 for c in text if ord(c) < 128) / len(text)


def generate_s2_mcq(proverb, meaning, language, rng, df_all, generator_model):
    """Generate an S2 MCQ from an English meaning."""
    cost_tracker.check()
    prompt_tokens_est = len(S2_USER_TEMPLATE.split()) + len(str(proverb).split()) + len(str(meaning).split()) + 50
    output_tokens_est = 200

    if cost_tracker.would_exceed(generator_model, prompt_tokens_est, output_tokens_est):
        error = f"Call would exceed ${COST_CAP_USD:.2f} cap (spent ${cost_tracker.spent:.4f})."
        safe_print(f"  [S2 HARD_FALLBACK] {generator_model}: {error}")
        opts = _make_s2_fallback(proverb, language, df_all, rng)
        _log_raw("generation", generator_model, "S2", language, proverb, meaning,
                 "", None, "hard_fallback", error=error)
        return opts, {"status": "hard_fallback", "error": error, "fallback_count": 0, "failure_weight": 2}

    user_prompt = S2_USER_TEMPLATE.format(
        correct_meaning=meaning, proverb=proverb, language=language
    )
    messages = [
        {"role": "system", "content": S2_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    raw_text = None
    finish_reason = None
    try:
        resp = openrouter_chat(generator_model, messages, max_tokens=MAX_TOKENS_GEN, response_format=None)
        text = extract_text(resp)
        raw_text = text
        finish_reason = extract_finish_reason(resp)
        prompt_tok, out_tok = extract_usage(resp)
        cost_tracker.add(generator_model, prompt_tok or prompt_tokens_est, out_tok,
                         f"S2-gen-{generator_model}-{language}")

        if not text or not text.strip():
            raise ValueError("Empty response content")
        if finish_reason == "length":
            raise ValueError("Truncated response (finish_reason=length)")

        opts = parse_options(text)
        if opts is None:
            raise ValueError(f"Could not parse S2 options. finish_reason={finish_reason}")
        if has_meta_text(opts):
            raise ValueError(f"Parsed S2 options contain meta-text / markdown: {opts!r}")
        if language and language.lower() == "yoruba" and has_yoruba_english_idiom(opts):
            raise ValueError(f"Yoruba S2 options contain a generic English idiom: {opts!r}")
    except Exception as e:
        is_hard = (finish_reason == "length" or raw_text is None or not str(raw_text).strip())
        weight = 2 if is_hard else 1
        status = "hard_fallback" if is_hard else "parse_fallback"
        safe_print(f"  [S2 {status.upper()}] {generator_model}: {e}")
        opts = _make_s2_fallback(proverb, language, df_all, rng)
        _log_raw("generation", generator_model, "S2", language, proverb, meaning,
                 raw_text, finish_reason, status, error=str(e))
        return opts, {"status": status, "error": str(e), "fallback_count": 0, "failure_weight": weight}

    # Force the gold proverb at index 0.
    opts[0] = str(proverb).strip()

    validated = [opts[0]]
    fallback_count = 0
    seen = {opts[0].strip().lower()}
    correct_lower = opts[0].strip().lower()

    for d in opts[1:]:
        d = str(d).strip()
        replaced = False

        if not d:
            replaced = True
        elif option_has_meta_text(d):
            replaced = True
        elif d.strip().lower() == correct_lower:
            replaced = True
        elif jaccard(d, opts[0]) > 0.5:
            replaced = True
        elif language != "English" and _ascii_ratio(d) > 0.7:
            replaced = True
        elif d.strip().lower() in seen:
            replaced = True

        if replaced:
            fallback_count += 1
            alt = proverb_negative_sample(proverb, language, df_all, rng, n=1)[0]
            d = str(alt).strip()
            # If the fallback still collides, draw another.
            attempts = 0
            while d.strip().lower() in seen and attempts < 5:
                alt = proverb_negative_sample(proverb, language, df_all, rng, n=1)[0]
                d = str(alt).strip()
                attempts += 1

        validated.append(d)
        seen.add(d.strip().lower())

    status = "generated" if fallback_count == 0 else ("partial" if fallback_count < 3 else "length_fallback")
    _log_raw("generation", generator_model, "S2", language, proverb, meaning,
             raw_text, finish_reason, status)
    return validated, {"status": status, "fallback_count": fallback_count, "failure_weight": 0}


# ── MCQ assembly ────────────────────────────────────────────────────────────

def assemble_mcq(opts, counter_name="S1"):
    """Place the correct answer at the next position in a round-robin A-D cycle.

    counter_name must be "S1" or "S2"; the two counters are independent so
    that separate generation loops do not create position-bias artifacts.
    """
    global S1_POSITION_COUNTER, S2_POSITION_COUNTER
    labels = ["A", "B", "C", "D"]
    if counter_name == "S2":
        correct_pos = S2_POSITION_COUNTER % 4
        S2_POSITION_COUNTER += 1
    else:
        correct_pos = S1_POSITION_COUNTER % 4
        S1_POSITION_COUNTER += 1
    distractors = opts[1:]
    ordered = distractors[:correct_pos] + [opts[0]] + distractors[correct_pos:]
    return {labels[i]: ordered[i] for i in range(4)}, labels[correct_pos]


def has_duplicate_options(options_dict):
    normalized = [re.sub(r"\s+", " ", v.strip().lower()) for v in options_dict.values()]
    return len(set(normalized)) < len(normalized)


# ── Choice extraction & parser self-test ────────────────────────────────────

def extract_choice(text):
    """Extract a single A-D choice. Normalise output to uppercase A-D or None."""
    if not text:
        return None
    text = str(text).strip()

    text = REASONING_TAGS.sub("", text)
    text = re.sub(r"```(?:json|markdown)?\s*", "", text)
    text = re.sub(r"```", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"[\[\]{}\"']", " ", text)
    text = re.sub(r"\b(?:json|markdown|text)\b", "", text, flags=re.IGNORECASE)
    text = text.strip()
    if not text:
        return None

    answer_patterns = [
        r"the\s+(?:best|correct|right)\s+answer\s+is\s+([A-D])\b",
        r"(?:best|correct|right)\s+answer\s*[:=]?\s*([A-D])\b",
        r"final answer\s*[:=]?\s*([A-D])\b",
        r"answer\s*[:=]\s*([A-D])\b",
        r"answer is\s+([A-D])\b",
        r"choice\s*[:=]?\s*([A-D])\b",
        r"option\s*[:=]?\s*([A-D])\b",
        r"\b([A-D])\s*(?:is\s+(?:correct|right|the\s+best))\b",
        r'\{\s*"?answer"?\s*[:=]\s*"?([A-D])"?\s*\}',
    ]
    for pat in answer_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            return matches[-1].upper()

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        for line in (lines[-1], lines[0]):
            if re.fullmatch(r"[A-Da-d]", line):
                return line.upper()
            m = re.match(r"(?:answer|choice|option)?[:\s]*\(?([A-Da-d])\)?[\.\):]?\s*$", line, re.IGNORECASE)
            if m:
                return m.group(1).upper()

    marker_match = re.search(r"(?:^|\s|\()([A-Da-d])[\.\):](?=\s|$)", text)
    if marker_match:
        return marker_match.group(1).upper()

    for match in reversed(list(re.finditer(r"\b([A-Da-d])\b", text))):
        s, e = match.start(), match.end()
        if match.group(1).lower() == 'a' and e < len(text) and text[e].isalpha() and text[e].islower():
            continue
        if re.match(r"\s*[,;:]\s*[A-Da-d]", text[e:]):
            continue
        return match.group(1).upper()
    return None


def parser_self_test():
    """Catch parser regressions before any API spend."""
    opt_cases = [
        ('["A", "B", "C", "D"]', ["A", "B", "C", "D"]),
        ("```json\n[\"A\", \"B\", \"C\", \"D\"]\n```", ["A", "B", "C", "D"]),
        ('{"0":"A", "1":"B", "2":"C", "3":"D"}', ["A", "B", "C", "D"]),
        ("<think>reasoning</think> [\"A\", \"B\", \"C\", \"D\"]", ["A", "B", "C", "D"]),
    ]
    for text, expected in opt_cases:
        got = parse_options(text)
        if got != expected:
            raise AssertionError(f"parse_options failed on {text!r}: expected {expected}, got {got}")

    letter_cases = [
        ("A", "A"),
        ("B.", "B"),
        ("(C)", "C"),
        ("Answer: D", "D"),
        ("<think>reasoning</think> Answer: C", "C"),
        ("The best answer is D because ...", "D"),
        ("Option B", "B"),
        ("A) is correct", "A"),
        ('```json\\n{\\"answer\\": \\"C\\"}\\n```', "C"),
        ("E", None),
        ("", None),
    ]
    for text, expected in letter_cases:
        got = extract_choice(text)
        if got != expected:
            raise AssertionError(f"extract_choice failed on {text!r}: expected {expected}, got {got}")

    safe_print("Parser self-test passed")


# ── Committee audit ─────────────────────────────────────────────────────────

def build_audit_prompt(strategy, question, options_dict):
    system_msg = "Reply ONLY with A, B, C, or D."
    if strategy == "S1":
        stem = f"What does this proverb mean?\n\nProverb: {question}"
    else:
        stem = f"Which proverb matches this meaning?\n\nMeaning: {question}"
    choice_text = "\n".join([f"{k}. {v}" for k, v in options_dict.items()])
    user_msg = f"{stem}\n\n{choice_text}\n\nAnswer with only the letter (A, B, C, or D)."
    return system_msg, user_msg


def audit_one_mcq(strategy, question, options_dict, correct_label, mcq_id, committee_pool):
    """Collect blind A-D votes from the active audit committee."""
    system_msg, user_msg = build_audit_prompt(strategy, question, options_dict)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    prompt_tokens_est = sum(len(str(m["content"]).split()) for m in messages) + 20

    votes = {}
    for model in list(committee_pool.active):
        if model not in committee_pool.active:
            continue
        cost_tracker.check()
        if cost_tracker.would_exceed(model, prompt_tokens_est, MAX_TOKENS_AUDIT):
            votes[model] = None
            committee_pool.record_failure(model, weight=2, reason="cost_would_exceed")
            _log_raw("audit", model, strategy, "", "", "", "", None,
                     "cost_skipped", error="cost_would_exceed", extracted=None)
            continue
        try:
            resp = openrouter_chat(model, messages, max_tokens=MAX_TOKENS_AUDIT)
            vote_text = extract_text(resp)
            finish_reason = extract_finish_reason(resp)
            prompt_tok, out_tok = extract_usage(resp)
            cost_tracker.add(model, prompt_tok or prompt_tokens_est, out_tok,
                             f"audit-{strategy}-{model}")

            if not vote_text or not vote_text.strip():
                raise ValueError("Empty audit response")
            if finish_reason == "length":
                raise ValueError("Truncated audit response (finish_reason=length)")

            vote = extract_choice(vote_text)
            if vote is None:
                committee_pool.record_failure(model, weight=1, reason="unparseable_vote")
            else:
                committee_pool.reset_failure_streak(model)
            votes[model] = vote
            _log_raw("audit", model, strategy, "", "", "", vote_text, finish_reason,
                     "voted", extracted=vote)
        except Exception as e:
            votes[model] = None
            committee_pool.record_failure(model, weight=2, reason=f"audit_exception:{type(e).__name__}")
            _log_raw("audit", model, strategy, "", "", "", "", None,
                     "exception", error=str(e), extracted=None)
    return votes


def compute_consensus(votes, correct_label, mcq_id=None):
    """Plurality consensus among auditors with deterministic tie-breaking."""
    valid = [v for v in votes.values() if v is not None]
    if not valid:
        return None, 0.0, 0
    counter = Counter(valid)
    ranked = counter.most_common()
    top_count = ranked[0][1]
    top_labels = [label for label, c in ranked if c == top_count]
    if len(top_labels) > 1:
        if mcq_id:
            tie_idx = int(hashlib.md5(str(mcq_id).encode("utf-8")).hexdigest(), 16) % len(top_labels)
        else:
            tie_idx = 0
        top_label = top_labels[tie_idx]
    else:
        top_label = top_labels[0]
    consensus_frac = top_count / len(valid)
    consensus_correct = 1 if top_label == correct_label else 0
    return top_label, consensus_frac, consensus_correct


# ── State persistence ───────────────────────────────────────────────────────

def save_state(generator_pool, audit_pool, generation_done=False, audit_done=False):
    """Persist pool state, cost, and position counter for resume."""
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost_spent": cost_tracker.spent,
        "cost_history": cost_tracker.history,
        "generator_pool": generator_pool.state_dict(),
        "audit_pool": audit_pool.state_dict(),
        "s1_position_counter": S1_POSITION_COUNTER,
        "s2_position_counter": S2_POSITION_COUNTER,
        "generation_done": generation_done,
        "audit_done": audit_done,
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def flush_outputs(s1_rows=None, s2_rows=None, audit_records=None):
    """Write intermediate CSVs without overwriting the final summary."""
    if s1_rows:
        pd.DataFrame(s1_rows).to_csv(os.path.join(OUTPUT_DIR, "mcqs_s1.csv"),
                                     index=False, encoding="utf-8-sig")
    if s2_rows:
        pd.DataFrame(s2_rows).to_csv(os.path.join(OUTPUT_DIR, "mcqs_s2.csv"),
                                     index=False, encoding="utf-8-sig")
    if audit_records:
        audit_df = pd.DataFrame(audit_records)
        for col in audit_df.columns:
            if col.startswith("vote_") or col.startswith("hit_"):
                audit_df[col] = audit_df[col].apply(lambda x: x if pd.notna(x) and x != "" else "")
        audit_df.to_csv(os.path.join(OUTPUT_DIR, "pilot2_eval_results.csv"),
                        index=False, encoding="utf-8-sig")
    if RAW_OUTPUTS:
        pd.DataFrame(RAW_OUTPUTS).to_csv(os.path.join(OUTPUT_DIR, "pilot2_raw_outputs.csv"),
                                         index=False, encoding="utf-8-sig")


# ── Preflight checks ────────────────────────────────────────────────────────

def preflight_check(df_sample, df_all, generator_pool, audit_pool):
    """FBI/CIA-style preflight: parsers, catalog, cheap probes, real-path probes, cost envelope."""
    safe_print("\n=== PREFLIGHT CHECK ===")
    safe_print(f"API key present: {bool(OPENROUTER_API_KEY)} ({len(OPENROUTER_API_KEY)} chars)")
    safe_print(f"Active generator pool: {generator_pool.active}")
    safe_print(f"Active audit pool: {audit_pool.active}")
    safe_print(f"Test sample size: {len(df_sample)} proverbs")
    safe_print(f"Cost cap: ${COST_CAP_USD}")

    # 1. Parser sanity check.
    parser_self_test()

    # 2. Live catalog + pricing refresh.
    live_models = []
    try:
        r = requests.get(MODELS_URL, timeout=30)
        r.raise_for_status()
        live_models = [m["id"] for m in r.json().get("data", [])]
        safe_print(f"Fetched live catalog: {len(live_models)} models")
    except Exception as e:
        safe_print(f"WARN: could not fetch live OpenRouter catalog: {e}")

    all_pool_models = list(dict.fromkeys(generator_pool.pool + audit_pool.pool))
    refresh_price_table(all_pool_models)

    generator_pool.filter_by_catalog(live_models)
    audit_pool.filter_by_catalog(live_models)

    active_models = list(dict.fromkeys(generator_pool.active + audit_pool.active))
    missing = [m for m in active_models if live_models and m not in live_models]
    if missing:
        safe_print(f"WARN: active models missing from live catalog: {missing}")
    else:
        safe_print("All active models found in live catalog (or catalog unavailable).")

    # 3. Cheap per-model API probe.
    safe_print("\n-- Cheap API probes (echo letter A) --")
    for model in list(generator_pool.active):
        if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
            generator_pool.record_failure(model, weight=2, reason="cheap_preflight_failed")
    for model in list(audit_pool.active):
        if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
            audit_pool.record_failure(model, weight=2, reason="cheap_preflight_failed")
    for model in generator_pool.pool + audit_pool.pool:
        if (model not in generator_pool.active and model not in generator_pool.benched
                and model not in audit_pool.active and model not in audit_pool.benched):
            if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
                if model in generator_pool.pool:
                    generator_pool.exclude(model, reason="cheap_preflight_failed")
                if model in audit_pool.pool:
                    audit_pool.exclude(model, reason="cheap_preflight_failed")

    if len(generator_pool.active) < MIN_ACTIVE_GENERATORS:
        safe_print(f"ABORT: only {len(generator_pool.active)} active generators (need {MIN_ACTIVE_GENERATORS}).")
        return False
    if len(audit_pool.active) < MIN_ACTIVE_COMMITTEE:
        safe_print(f"ABORT: only {len(audit_pool.active)} active auditors (need {MIN_ACTIVE_COMMITTEE}).")
        return False

    # 4. Real generation-path probes for S1 and S2.
    safe_print("\n-- Generator probes (real generation path) --")
    probe_rng = random.Random(SEED + 999)
    probe_row = df_sample.iloc[0]
    all_meanings = df_all["meaning"].dropna().unique().tolist()

    s1_probe_opts = None
    s2_probe_opts = None
    probed_generators = set()

    while True:
        remaining = [m for m in generator_pool.active if m not in probed_generators]
        if not remaining:
            break
        gen = remaining[0]
        probed_generators.add(gen)

        try:
            cost_tracker.check()
            s1_opts, s1_meta = generate_s1_mcq(
                probe_row["proverb"], probe_row["meaning"], probe_row["language"],
                probe_rng, all_meanings, df_all, gen
            )
            s2_opts, s2_meta = generate_s2_mcq(
                probe_row["proverb"], probe_row["meaning"], probe_row["language"],
                probe_rng, df_all, gen
            )
            bad = False
            if s1_meta.get("status") in ("hard_fallback", "parse_fallback") or len(s1_opts) != 4:
                safe_print(f"  [FAIL] {gen}: S1 probe status={s1_meta.get('status')} opts={s1_opts}")
                bad = True
            if s2_meta.get("status") in ("hard_fallback", "parse_fallback") or len(s2_opts) != 4:
                safe_print(f"  [FAIL] {gen}: S2 probe status={s2_meta.get('status')} opts={s2_opts}")
                bad = True
            if bad:
                generator_pool.record_failure(gen, weight=2, reason="preflight_generation_failed")
            else:
                generator_pool.reset_failure_streak(gen)
                s1_probe_opts = s1_opts
                s2_probe_opts = s2_opts
                safe_print(f"  [OK] {gen}: S1={s1_meta.get('status')}, S2={s2_meta.get('status')}")
        except Exception as e:
            safe_print(f"  [FAIL] {gen}: {e}")
            generator_pool.record_failure(gen, weight=2, reason=f"preflight_exception:{type(e).__name__}")

    if len(generator_pool.active) < MIN_ACTIVE_GENERATORS:
        safe_print(f"ABORT: only {len(generator_pool.active)} active generators after real-path probes.")
        return False
    if s1_probe_opts is None or s2_probe_opts is None:
        safe_print("ABORT: no generator produced usable S1/S2 probe options.")
        return False

    # 5. Real audit-path probe using the S1 probe options.
    safe_print("\n-- Audit probes (real audit path) --")
    probe_options_dict = {"A": s1_probe_opts[0], "B": s1_probe_opts[1],
                          "C": s1_probe_opts[2], "D": s1_probe_opts[3]}
    probed_auditors = set()

    while True:
        remaining = [m for m in audit_pool.active if m not in probed_auditors]
        if not remaining:
            break
        aud = remaining[0]
        probed_auditors.add(aud)
        try:
            cost_tracker.check()
            resp = openrouter_chat(aud, [
                {"role": "system", "content": "Reply ONLY with A, B, C, or D."},
                {"role": "user", "content": "Which option is correct?\n\n" +
                 "\n".join(f"{k}. {v}" for k, v in probe_options_dict.items())},
            ], max_tokens=MAX_TOKENS_AUDIT)
            vote_text = extract_text(resp)
            finish_reason = extract_finish_reason(resp)
            prompt_tok, out_tok = extract_usage(resp)
            cost_tracker.add(aud, prompt_tok or 100, out_tok, "audit-preflight")

            if not vote_text or not vote_text.strip():
                raise ValueError("Empty audit response")
            if finish_reason == "length":
                raise ValueError("Truncated audit response")
            vote = extract_choice(vote_text)
            if vote not in {"A", "B", "C", "D"}:
                audit_pool.record_failure(aud, weight=1, reason="preflight:unparseable_vote")
                safe_print(f"  [FAIL] {aud}: could not extract A-D vote (got {vote})")
            else:
                audit_pool.reset_failure_streak(aud)
                safe_print(f"  [OK] {aud}: vote={vote}")
        except Exception as e:
            safe_print(f"  [FAIL] {aud}: {e}")
            audit_pool.record_failure(aud, weight=2, reason=f"preflight_exception:{type(e).__name__}")

    if len(audit_pool.active) < MIN_ACTIVE_COMMITTEE:
        safe_print(f"ABORT: only {len(audit_pool.active)} active auditors after real-path probes.")
        return False

    # 6. Cost envelope estimate.
    n_mcqs = 2 * len(df_sample)  # S1 + S2
    gen_input_est = 400
    gen_output_est = 300
    audit_input_est = 300
    audit_output_est = 10
    gen_est = (
        sum(cost_tracker.estimate(m, gen_input_est, gen_output_est) for m in generator_pool.active)
        / len(generator_pool.active)
        * n_mcqs
    ) if generator_pool.active else 0.0
    audit_est = sum(cost_tracker.estimate(m, audit_input_est, audit_output_est) for m in audit_pool.active) * n_mcqs
    preflight_spent = cost_tracker.spent
    total_est = gen_est + audit_est + preflight_spent

    safe_print(f"\n-- Cost envelope --")
    safe_print(f"  Preflight spend so far: ${preflight_spent:.4f}")
    safe_print(f"  Estimated generation cost: ${gen_est:.4f}")
    safe_print(f"  Estimated audit cost: ${audit_est:.4f}")
    safe_print(f"  Estimated total: ${total_est:.4f} / ${COST_CAP_USD:.2f} cap")

    if total_est > COST_CAP_USD * 0.9:
        safe_print("ABORT: estimated cost exceeds 90% of cap.")
        return False
    if total_est > COST_CAP_USD * 0.5:
        safe_print("WARNING: estimated cost exceeds 50% of cap.")

    safe_print("PREFLIGHT PASSED\n")
    return True


# ── Main pipeline ───────────────────────────────────────────────────────────

def main():
    global generator_pool, audit_pool, cost_tracker, S1_POSITION_COUNTER, S2_POSITION_COUNTER

    safe_print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Pilot 2 v3")
    safe_print(f"Data dir: {DATA_DIR}")
    safe_print(f"Output dir: {OUTPUT_DIR}")
    safe_print(f"Cost cap: ${COST_CAP_USD}")

    df_all = load_proverbs()
    all_meanings = df_all["meaning"].dropna().unique().tolist()
    rng = random.Random(SEED)

    df_sample = sample_per_language(df_all, N_PER_LANG, SEED).reset_index(drop=True)
    safe_print(f"\nSampled {len(df_sample)} proverbs:")
    safe_print(df_sample.groupby("language").size().to_string())

    # Rehydrate state if available.
    generation_done = False
    audit_done = False
    if os.path.exists(STATE_PATH):
        safe_print(f"\nFound existing state file: {STATE_PATH}")
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
        generator_pool = ModelPool(GENERATOR_POOL, GENERATOR_STARTERS, "GENERATOR",
                                   state=state.get("generator_pool"))
        audit_pool = ModelPool(AUDIT_POOL, AUDIT_STARTERS, "AUDIT",
                               state=state.get("audit_pool"))
        cost_tracker = CostTracker(
            COST_CAP_USD,
            spent=state.get("cost_spent", 0.0),
            history=state.get("cost_history", [])
        )
        S1_POSITION_COUNTER = state.get("s1_position_counter", 0)
        S2_POSITION_COUNTER = state.get("s2_position_counter", 0)
        generation_done = state.get("generation_done", False)
        audit_done = state.get("audit_done", False)
        safe_print(f"Rehydrated cost: ${cost_tracker.spent:.4f}")
        safe_print(f"Active generators: {generator_pool.active}")
        safe_print(f"Active auditors: {audit_pool.active}")

    # Preflight before any expensive loop.
    if not generation_done:
        if not preflight_check(df_sample, df_all, generator_pool, audit_pool):
            save_state(generator_pool, audit_pool, generation_done, audit_done)
            raise RuntimeError("Preflight checks failed. Aborting before main spend.")
        save_state(generator_pool, audit_pool, generation_done, audit_done)

    if not generator_pool.active and not generation_done:
        raise RuntimeError("No active generator available.")

    # Round-robin index for actually rotating across active generators.
    _generator_rotation_index = 0
    generator_model = generator_pool.active[0] if generator_pool.active else None

    # Generate S1 and S2 MCQs.
    s1_rows, s2_rows = [], []
    if not generation_done:
        safe_print("\n=== Generating S1 & S2 MCQs ===")
        for idx, row in df_sample.iterrows():
            active_gens = generator_pool.active
            if not active_gens:
                raise RuntimeError("No active generators remaining.")
            generator_model = active_gens[_generator_rotation_index % len(active_gens)]
            _generator_rotation_index += 1

            # S1
            s1_opts, s1_meta = generate_s1_mcq(
                row["proverb"], row["meaning"], row["language"],
                rng, all_meanings, df_all, generator_model
            )
            s1_options, s1_answer = assemble_mcq(s1_opts, counter_name="S1")
            s1_rows.append({
                "sample_id": row["sample_id"],
                "language": row["language"],
                "strategy": "S1",
                "generator_model": generator_model,
                "source_proverb": row["proverb"],
                "gold": row["meaning"],
                "distractors": json.dumps(s1_opts[1:], ensure_ascii=False),
                "fallback": s1_meta.get("status", "unknown") != "generated",
                "Choice_A": s1_options["A"],
                "Choice_B": s1_options["B"],
                "Choice_C": s1_options["C"],
                "Choice_D": s1_options["D"],
                "Answer": s1_answer,
                "generation_status": s1_meta.get("status", "unknown"),
                "raw_model_output": raw_model_output_for("generation", generator_model, "S1",
                                                           row["proverb"], row["meaning"]),
            })

            # S2
            s2_opts, s2_meta = generate_s2_mcq(
                row["proverb"], row["meaning"], row["language"],
                rng, df_all, generator_model
            )
            s2_options, s2_answer = assemble_mcq(s2_opts, counter_name="S2")
            s2_rows.append({
                "sample_id": row["sample_id"],
                "language": row["language"],
                "strategy": "S2",
                "generator_model": generator_model,
                "source_proverb": row["proverb"],
                "gold": row["meaning"],
                "distractors": json.dumps(s2_opts[1:], ensure_ascii=False),
                "fallback": s2_meta.get("status", "unknown") != "generated",
                "Choice_A": s2_options["A"],
                "Choice_B": s2_options["B"],
                "Choice_C": s2_options["C"],
                "Choice_D": s2_options["D"],
                "Answer": s2_answer,
                "generation_status": s2_meta.get("status", "unknown"),
                "raw_model_output": raw_model_output_for("generation", generator_model, "S2",
                                                           row["proverb"], row["meaning"]),
            })

            if idx % 10 == 0 or idx == len(df_sample) - 1:
                flush_outputs(s1_rows, s2_rows)
                save_state(generator_pool, audit_pool, generation_done, audit_done)
                safe_print(f"  Generated {idx + 1}/{len(df_sample)} proverbs; cost: ${cost_tracker.spent:.4f}")

        generation_done = True
        flush_outputs(s1_rows, s2_rows)
        save_state(generator_pool, audit_pool, generation_done, audit_done)

    s1_df = pd.read_csv(os.path.join(OUTPUT_DIR, "mcqs_s1.csv"), encoding="utf-8-sig")
    s2_df = pd.read_csv(os.path.join(OUTPUT_DIR, "mcqs_s2.csv"), encoding="utf-8-sig")

    # Audit generated MCQs.
    audit_records = []
    if not audit_done:
        safe_print(f"\n=== Running committee audit with {audit_pool.active} ===")
        for df, strategy in [(s1_df, "S1"), (s2_df, "S2")]:
            for _, row in df.iterrows():
                question = row["source_proverb"] if strategy == "S1" else row["gold"]
                options_dict = {
                    "A": row["Choice_A"],
                    "B": row["Choice_B"],
                    "C": row["Choice_C"],
                    "D": row["Choice_D"],
                }
                mcq_id = f"{strategy}_{row['language']}_{row['sample_id']}"
                votes = audit_one_mcq(strategy, question, options_dict,
                                      row["Answer"], mcq_id, audit_pool)
                consensus_label, consensus_frac, consensus_correct = compute_consensus(
                    votes, row["Answer"], mcq_id=mcq_id
                )
                rec = {
                    "mcq_id": mcq_id,
                    "strategy": strategy,
                    "language": row["language"],
                    "correct_label": row["Answer"],
                    "consensus_label": consensus_label,
                    "consensus_frac": consensus_frac,
                    "consensus_correct": consensus_correct,
                }
                for model, vote in votes.items():
                    rec[f"vote_{model.replace('/', '_')}"] = vote
                    rec[f"hit_{model.replace('/', '_')}"] = int(vote == row["Answer"]) if vote else None
                audit_records.append(rec)

                if len(audit_pool.active) == 0:
                    flush_outputs(s1_rows, s2_rows, audit_records)
                    save_state(generator_pool, audit_pool, generation_done, audit_done)
                    raise RuntimeError("No active auditors remaining. Audit halted.")

                if len(audit_records) % 20 == 0:
                    flush_outputs(s1_rows, s2_rows, audit_records)
                    save_state(generator_pool, audit_pool, generation_done, audit_done)
                    safe_print(f"  Audited {len(audit_records)} MCQs; cost: ${cost_tracker.spent:.4f}")

        audit_done = True
        flush_outputs(s1_rows, s2_rows, audit_records)
        save_state(generator_pool, audit_pool, generation_done, audit_done)

    audit_df = pd.read_csv(os.path.join(OUTPUT_DIR, "pilot2_eval_results.csv"), encoding="utf-8-sig")

    # Summaries.
    summary_by_lang = (
        audit_df.groupby(["strategy", "language"])
        .agg(
            n=("consensus_correct", "size"),
            consensus_accuracy=("consensus_correct", "mean"),
            mean_consensus_frac=("consensus_frac", "mean"),
        )
        .reset_index()
    )
    summary_by_lang["consensus_accuracy"] = summary_by_lang["consensus_accuracy"].round(4)
    summary_by_lang["mean_consensus_frac"] = summary_by_lang["mean_consensus_frac"].round(4)

    overall = (
        audit_df.groupby("strategy")
        .agg(
            n=("consensus_correct", "size"),
            consensus_accuracy=("consensus_correct", "mean"),
        )
        .reset_index()
    )
    overall["consensus_accuracy"] = overall["consensus_accuracy"].round(4)

    per_model_rows = []
    for strategy in ["S1", "S2"]:
        sub = audit_df[audit_df["strategy"] == strategy]
        for model in audit_pool.active + audit_pool.benched:
            col = f"hit_{model.replace('/', '_')}"
            if col not in sub.columns:
                continue
            valid = sub[col].notna() & (sub[col].astype(str) != "")
            if valid.sum() == 0:
                continue
            per_model_rows.append({
                "strategy": strategy,
                "model": model,
                "accuracy": sub.loc[valid, col].mean(),
                "n": int(valid.sum()),
            })
    per_model_df = pd.DataFrame(per_model_rows)

    safe_print("\n=== Per-strategy consensus accuracy ===")
    safe_print(overall.to_string(index=False))
    safe_print("\n=== Per-strategy/language consensus accuracy ===")
    safe_print(summary_by_lang.to_string(index=False))

    summary_payload = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "n_per_language": N_PER_LANG,
        "data_dir": DATA_DIR,
        "generator_model": generator_model,
        "generator_pool": generator_pool.state_dict(),
        "audit_pool": audit_pool.state_dict(),
        "cost_cap_usd": COST_CAP_USD,
        "total_estimated_cost_usd": round(cost_tracker.spent, 6),
        "overall_consensus": json.loads(overall.to_json(orient="records")),
        "per_strategy_language": json.loads(summary_by_lang.to_json(orient="records")),
        "per_model_accuracy": json.loads(per_model_df.to_json(orient="records")),
        "cost_history": cost_tracker.history,
    }
    summary_path = os.path.join(OUTPUT_DIR, "pilot2_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, ensure_ascii=False, indent=2)

    safe_print(f"\nSaved outputs to {OUTPUT_DIR}")
    safe_print(f"Total estimated cost: ${cost_tracker.spent:.4f} / ${COST_CAP_USD:.2f}")


def raw_model_output_for(stage, model, strategy, proverb, meaning):
    """Recover the raw model output logged during generation for a given key."""
    for entry in reversed(RAW_OUTPUTS):
        if (entry.get("stage") == stage and entry.get("model") == model
                and entry.get("strategy") == strategy
                and entry.get("proverb") == proverb and entry.get("meaning") == meaning):
            return entry.get("raw_model_output", "")
    return ""


if __name__ == "__main__":
    main()
