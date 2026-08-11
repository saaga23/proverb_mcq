"""
OpenRouter Pilot 1 TEST variant — multi-model generator shakedown with dynamic
model-pool substitutions (football-style bench/sub system).

Purpose:
  Low-cost, low-risk shakedown of the Pilot 1 generation/audit pipeline before
  scaling to the full S2 evaluation. Runs adversarial prompt variants and
  anti-contamination / anti-shortcut safeguards, with multiple cheap-to-mid
  generators side-by-side and an expanded audit committee. If a model fails
  repeatedly it is benched and a substitute is brought in automatically; all
  state is persisted so runs can resume.

Generators under test (starters) — reduced to 3 fastest/reliable models so the
local N=2 run finishes within the one-hour background timeout:
  - qwen/qwen3.7-max       ($1.25 / $3.75 per 1M)  -- most reliable in N=2 run
  - google/gemma-4-31b-it  ($0.12 / $0.36 per 1M)  -- reliable, good consensus accuracy
  - google/gemini-2.5-flash ($0.15 / $0.60 per 1M) -- reliable substitute promoted to starter

Kept as substitutes:
  - anthropic/claude-sonnet-4 ($3 / $15 per 1M)
  - openai/gpt-4.1-mini    ($0.40 / $1.60 per 1M)

Removed from starters after N=2 run (high failure or high confident-wrong rate):
  - meta-llama/llama-4-maverick (67% bad rows, 61% high-consensus-wrong)
  - deepseek/deepseek-v4-pro    (100% bad rows, benched during generation)
  - qwen/qwen3.5-397b-a17b      (benched during preflight)

Audit committee (starters) — kept disjoint from generators to avoid audit contamination:
  - meta-llama/llama-3.3-70b-instruct   (proven in v2.1 smoke test, 47.8% hit rate)
  - mistralai/mistral-small-3.2-24b-instruct (proven, 54.4% hit rate)
  - google/gemma-3-27b-it               (proven, 46.7% hit rate)
  - deepseek/deepseek-v3.2              (proven substitute, 66-80% hit rate; 4th auditor)

Self-critic (generation-time only) — DISABLED for the next smoke test because it
always triggered rewrites without improving shortcut-resistance:
  - deepseek/deepseek-v3.2 (currently benched via USE_SELF_CRITIQUE = False)

Hardening vs v2:
  - Dynamic ModelPool: repeated failures bench a model and promote a substitute.
  - State saved to pool_state.json for resume after crashes or substitutions.
  - max_tokens is OPTIONAL for generation (set to None to avoid provider
    minimum-token / truncation edge cases). Audit still caps output at 256.
  - openrouter_chat falls back through payload variants on 400/422:
    (max_tokens present → omitted → JSON mode omitted).
  - Aggressive preflight probes every active generator and auditor and
    keeps probing substitutes until the active roster is healthy.
  - Live-catalog check against OpenRouter /api/v1/models.
  - Raw-response logging captures finish_reason and provider errors.
  - Post-parse meta-text rejection prevents model headings from leaking into options.

Outputs:
  pilot1_test_generated_mcqs.csv     -- MCQs by generator, variant, language
  pilot1_test_audit_results.csv      -- raw blind-audit votes
  pilot1_test_prompt_comparison.csv  -- per-generator/variant consensus accuracy
  pilot1_test_raw_outputs.csv        -- full raw model outputs for forensics
  pilot1_test_summary.json           -- run summary + cost history + pool state
  pool_state.json                    -- resume state (active/benched pools, cost)
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
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless Kaggle runs.
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

# Lazy-loaded multilingual embedding model for semantic-distance filtering.
_EMBEDDING_MODEL = None
_EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Lightweight NLI model for detecting paraphrase/entailment between distractors
# and the correct meaning. Options are English, so an English NLI model suffices.
_NLI_MODEL = None
_NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-xsmall"
USE_NLI_FILTER = True
NLI_ENTAILMENT_THRESHOLD = 0.60
# Distractors flagged by NLI are only rejected when they are also close in embedding
# space. This suppresses NLI false positives on unrelated short phrases.
NLI_EMBEDDING_GUARD = 0.55
# v65 — language-specific embedding guard. Arabic/Yoruba use a tighter guard because
# their glosses are shorter/literal and auditors are easily misled by near-paraphrase
# distractors. English uses a slightly looser guard so that more subtle near-paraphrase
# distractors survive, lowering perfect-consensus without becoming paraphrases.
NLI_EMBEDDING_GUARD_BY_LANGUAGE = {
    "default": 0.55,
    "english": 0.58,
    "arabic": 0.45,
    "yoruba": 0.45,
}

def _nli_embedding_guard(language):
    return NLI_EMBEDDING_GUARD_BY_LANGUAGE.get((language or "").lower(), NLI_EMBEDDING_GUARD_BY_LANGUAGE["default"])

# v67 — length parity: restored to ±35% vs the median, with ±45% relaxed all-within.
# v66's ±45%/±55% relaxation reduced length_fallback but inflated partial items by
# letting more NLI/corpus replacements through. The stricter band is restored.
LENGTH_CHECK_THRESHOLD = 0.35
LENGTH_RELAXED_THRESHOLD = 0.45

# v62 — correct-meaning leak threshold is language-specific. English glosses are
# longer and more likely to contain legitimate hard negatives that share words
# with the correct meaning, so the threshold is raised.
LEAK_THRESHOLD_BY_LANGUAGE = {
    "default": 0.80,
    "english": 0.90,
}

# v64 — gold-meaning curation for all languages. Rewrite literal/awkward glosses
# into natural English before option generation; Yoruba and Arabic especially need
# this because their dataset glosses are often literal translations.
USE_GOLD_MEANING_CURATION = True
GOLD_CURATION_MODEL = "openai/gpt-4.1-nano"

# v67 — LLM-based fallback distractor generator (disabled by default for the frozen
# config; available as an optional ablation). The corpus-based fallback sampler can
# produce generic or culturally mismatched distractors that drive partial+fallback
# and high-consensus-wrong. A cheap, proverb-specific LLM call generates a single
# hard-negative distractor on demand, then the same length/semantic/NLI/blocklist
# filters are applied. Corpus sampling remains as the default fallback.
USE_LLM_FALLBACK = True  # v69 ablation: LLM-based fallback distractor generator enabled
FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"
_LLM_FALLBACK_CACHE = {}
_LLM_FALLBACK_PROVERB = None
_LLM_FALLBACK_VARIANT = None
_LLM_FALLBACK_USED = 0
_LLM_FALLBACK_REJECTED = 0


def _set_llm_fallback_context(proverb, variant_name):
    """Set per-item context so the fallback generator can be proverb-specific."""
    global _LLM_FALLBACK_PROVERB, _LLM_FALLBACK_VARIANT
    _LLM_FALLBACK_PROVERB = proverb
    _LLM_FALLBACK_VARIANT = variant_name


def _clear_llm_fallback_context():
    global _LLM_FALLBACK_PROVERB, _LLM_FALLBACK_VARIANT
    _LLM_FALLBACK_PROVERB = None
    _LLM_FALLBACK_VARIANT = None


def generate_llm_fallback_distractor(reference_meaning, all_meanings, rng, language=None, exclude=None, max_attempts=3):
    """
    Generate a single proverb-specific hard-negative distractor using a cheap LLM.

    The distractor must be:
      - a plausible but incorrect interpretation of the current proverb,
      - semantically distinct from the correct meaning (embedding band),
      - not a generic English idiom or surface shortcut,
      - length-matched to the other options,
      - not in the `exclude` set.

    Returns a candidate string. If generation fails validation after all attempts,
    falls back to the corpus sampler.
    """
    global _LLM_FALLBACK_PROVERB, _LLM_FALLBACK_VARIANT, _LLM_FALLBACK_USED, _LLM_FALLBACK_REJECTED
    proverb = _LLM_FALLBACK_PROVERB
    variant_name = _LLM_FALLBACK_VARIANT or "unknown"

    if not OPENROUTER_API_KEY or not proverb:
        # Context missing or no API key: break potential recursion and use corpus sampler.
        return semantically_distinct_negative_sample(
            reference_meaning, all_meanings, rng, n=1, language=language, exclude=exclude, use_llm=False
        )[0]

    cache_key = (
        str(proverb).strip().lower(),
        str(reference_meaning).strip().lower(),
        str(language or "").lower(),
        str(variant_name).lower(),
        tuple(sorted({_normalized_option(x) for x in (exclude or [])})),
    )
    if cache_key in _LLM_FALLBACK_CACHE:
        return _LLM_FALLBACK_CACHE[cache_key]

    # Build a short prompt that asks for exactly one wrong option.
    lang_note = ""
    if language and language.lower() == "yoruba":
        lang_note = " This is a Yoruba proverb; stay inside a Yoruba cultural frame."
    elif language and language.lower() == "arabic":
        lang_note = " This is an Arabic proverb; avoid generic English idioms."

    base_prompt = (
        "You are writing a hard multiple-choice distractor for a proverb.\n"
        f"Proverb ({language or 'unknown'}): {proverb}{lang_note}\n"
        f"Correct meaning: {reference_meaning}\n\n"
        "Write ONE incorrect but plausible meaning that a reader might believe the proverb has. "
        "It must NOT be a paraphrase, synonym, or obvious opposite of the correct meaning. "
        "It must NOT be a generic English idiom or proverb (e.g., 'a bird in the hand', 'charity begins at home'). "
        f"Keep it roughly the same length as the correct meaning ({len(str(reference_meaning))} characters). "
        "Output ONLY the single distractor sentence, with no label, numbering, or explanation."
    )

    prompt_tokens_est = len(base_prompt.split()) + 30
    output_tokens_est = 60

    # If cost cap is tight, skip the LLM call and use corpus fallback.
    if cost_tracker.would_exceed(FALLBACK_GENERATOR_MODEL, prompt_tokens_est, output_tokens_est):
        return semantically_distinct_negative_sample(
            reference_meaning, all_meanings, rng, n=1, language=language, exclude=exclude, use_llm=False
        )[0]

    exclude_norm = {_normalized_option(x) for x in (exclude or [])}
    exclude_norm.add(_normalized_option(reference_meaning))

    for attempt in range(max_attempts):
        # Add a tiny instruction perturbation per attempt to diversify output.
        perturb = ""
        if attempt == 1:
            perturb = " Make the distractor focus on a different actor or cause than the correct meaning."
        elif attempt == 2:
            perturb = " Make the distractor change the scope from individual to community, or vice versa."
        prompt = base_prompt + perturb

        try:
            resp = openrouter_chat(
                FALLBACK_GENERATOR_MODEL,
                [{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.0,
            )
            text = extract_text(resp).strip().strip('"').strip("'")
            prompt_tok, out_tok = extract_usage(resp)
            cost_tracker.add(FALLBACK_GENERATOR_MODEL, prompt_tok or prompt_tokens_est, out_tok or output_tokens_est, "fallback_generator")

            if not text or len(text) < 12 or not text[0].isupper():
                continue

            # Validate against the same filters used for generator outputs.
            if _has_meta_text_single(text):
                continue
            if has_generic_english_idiom([text]):
                continue
            if _is_offensive_or_inappropriate(text):
                continue
            if _normalized_option(text) in exclude_norm:
                continue

            # Reject if it echoes or near-paraphrases the correct meaning.
            leak_threshold = LEAK_THRESHOLD_BY_LANGUAGE.get(
                (language or "").lower(), LEAK_THRESHOLD_BY_LANGUAGE["default"]
            )
            if _is_correct_meaning_leak(text, reference_meaning, threshold=leak_threshold):
                continue

            # Reject if it is too close/far in embedding space from the correct meaning.
            emb = _load_embedding_model()
            ref_vec = emb.encode(str(reference_meaning))
            cand_vec = emb.encode(text)
            sim = float(np.dot(ref_vec, cand_vec) / (np.linalg.norm(ref_vec) * np.linalg.norm(cand_vec)))
            band = SEMANTIC_DISTANCE_BAND.get((language or "").lower(), SEMANTIC_DISTANCE_BAND["default"])
            if sim > band["max"]:
                continue

            # Reject if NLI flags it as entailing/entailed by the correct meaning.
            if USE_NLI_FILTER:
                forward = _nli_entailment_score(text, reference_meaning)
                backward = _nli_entailment_score(reference_meaning, text)
                nli_flagged = forward >= NLI_ENTAILMENT_THRESHOLD or backward >= NLI_ENTAILMENT_THRESHOLD
                if nli_flagged:
                    guard = _nli_embedding_guard(language)
                    if sim > guard:
                        continue

            # Length parity against the reference meaning (same ±threshold as main pipeline).
            if not _length_ratio_ok(text, reference_meaning, lo=1 - LENGTH_CHECK_THRESHOLD, hi=1 + LENGTH_CHECK_THRESHOLD):
                continue

            _LLM_FALLBACK_USED += 1
            _LLM_FALLBACK_CACHE[cache_key] = text
            safe_print(f"  [LLM FALLBACK] generated distractor: {text!r}")
            return text
        except Exception as e:
            safe_print(f"  [LLM FALLBACK] attempt {attempt + 1} failed: {e}")
            continue

    _LLM_FALLBACK_REJECTED += 1

    # All attempts failed — fall back to corpus sampler (disable LLM fallback to avoid recursion).
    return semantically_distinct_negative_sample(
        reference_meaning, all_meanings, rng, n=1, language=language, exclude=exclude, use_llm=False
    )[0]


# v62 — fallback quality guard. Reject corpus fallbacks that contain vulgar,
# sexual, or otherwise inappropriate content.
_FALLBACK_OFFENSIVE_BLOCKLIST = {
    "penis", "vagina", "sex", "sexual", "fuck", "fucking", "shit", "damn",
    "bitch", "asshole", "bastard", "rape", "rapist", "incest", "masturbate",
    "masturbation", "orgasm", "porn", "whore", "slut", "dick", "cock", "cunt",
    "pussy", "tits", "boobs", "nude", "naked", "prostitute", "brothel",
}


def _load_embedding_model():
    """Load a lightweight multilingual sentence encoder once and cache it."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        safe_print("sentence-transformers not found; installing...")
        import subprocess, sys
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q", "sentence-transformers"
        ])
        from sentence_transformers import SentenceTransformer
    # Use the project model_cache directory so Kaggle downloads persist across runs.
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = os.getcwd()
    cache_dir = os.environ.get("HF_HOME") or os.path.join(here, "model_cache")
    safe_print(f"Loading embedding model {_EMBEDDING_MODEL_NAME} ...")
    _EMBEDDING_MODEL = SentenceTransformer(_EMBEDDING_MODEL_NAME, cache_folder=cache_dir)
    safe_print("Embedding model loaded.")
    return _EMBEDDING_MODEL


def _load_nli_model():
    """Load a lightweight NLI cross-encoder once and cache it. Returns None on failure."""
    global _NLI_MODEL
    if _NLI_MODEL is not None:
        return _NLI_MODEL
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        safe_print("sentence-transformers not found; NLI filter disabled.")
        return None
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = os.getcwd()
    cache_dir = os.environ.get("HF_HOME") or os.path.join(here, "model_cache")
    try:
        safe_print(f"Loading NLI model {_NLI_MODEL_NAME} ...")
        _NLI_MODEL = CrossEncoder(_NLI_MODEL_NAME, max_length=256, device="cpu", cache_dir=cache_dir)
        safe_print("NLI model loaded.")
    except Exception as e:
        safe_print(f"NLI model failed to load: {e}. Disabling NLI filter.")
        _NLI_MODEL = False  # sentinel: do not retry
    return _NLI_MODEL


# ── Configuration ───────────────────────────────────────────────────────────

N_PER_LANG = 5                       # frozen v67 config: scale to 5 per language first, then 15 after confirming quality holds
SEED = 20260615
COST_CAP_USD = 5.0
TEMPERATURE = 0.0

# Optional with-proverb baseline audit. Adds one extra API call per MCQ; keep
# False for the core smoke test to save budget, then enable for paper results.
RUN_WITH_PROVERB_BASELINE = False

# Generation: use a high max_tokens ceiling to avoid truncation, while still
# leaving payload fallbacks if a provider rejects the parameter. The earlier
# 8-token audit floor and 600-token generation cap caused empty-content / parse
# failures; 2048 is safely below context limits for these short prompts.
MAX_TOKENS_GEN = 2048

# JSON Schema for structured generation: exact array of 4 strings.
# Used for models (e.g., openai/gpt-5) that support strict structured outputs.
OPTIONS_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "proverb_options",
        "strict": True,
        "schema": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 4,
            "maxItems": 4,
        },
    },
}

# Audit: we only need one letter, but set a generous ceiling to avoid errors.
MAX_TOKENS_AUDIT = 256

# Self-critique loop configuration.
# A frozen critic model audits freshly generated options; if it picks the correct
# answer, the generator is asked to rewrite the distractors to be harder.
# The critic is deliberately NOT in the audit committee to avoid contaminating
# the final blind audit.
CRITIC_MODEL = "deepseek/deepseek-v3.2"
USE_SELF_CRITIQUE = False
MAX_SELF_CRITIQUE_ROUNDS = 1

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"

# Minimum healthy active roster. If preflight or runtime substitutions drop us
# below these numbers the run aborts.
MIN_ACTIVE_GENERATORS = 2
MIN_ACTIVE_COMMITTEE = 2

# Ranked model pools. Starters are the first N entries; everything afterwards is
# a substitute that can be promoted if a starter is benched.
GENERATOR_POOL = [
    # Starters — chosen after Pilot 1 N=2 run (2026-06-20).
    "qwen/qwen3.7-max",
    "google/gemma-4-31b-it",
    "google/gemini-2.5-flash",
    # Primary substitutes — promoted if a starter is benched.
    # gemini-2.5-pro and gpt-4.1-mini are more reliable than claude-sonnet-4,
    # which had parse/reliability issues in earlier runs.
    "google/gemini-2.5-pro",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1-nano",
    # Higher-cost / lower-reliability models used only as emergency substitutes.
    "anthropic/claude-sonnet-4",
    "qwen/qwen3.5-397b-a17b",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-v4-pro",
]
GENERATOR_STARTERS = 3

COMMITTEE_POOL = [
    # Starters — kept disjoint from the generator pool to avoid audit contamination.
    # Selection rationale (June 19 run evidence):
    #   llama-3.3-70b-instruct  : 47.8% hit rate, 0% missing votes
    #   mistral-small-3.2-24b   : 54.4% hit rate, 0% missing votes
    #   gemma-3-27b-it          : 46.7% hit rate, 0% missing votes
    #   deepseek/deepseek-v3.2  : promoted from substitute; reliable, 66-80% hit rate
    # Removed from starters:
    #   qwen/qwen3-32b          : 97.8% missing votes due to ValueError in extract_choice
    #   anthropic/claude-3.5-haiku : EOL on OpenRouter/AWS Bedrock (404)
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct",
    "google/gemma-3-27b-it",
    "deepseek/deepseek-v3.2",
    # Substitutes — also disjoint from the generator pool.
    # Removed gpt-4o-mini (37.9% hit rate, weak) and llama-3.1-405b (404 Not Found).
    "deepseek/deepseek-v3.2",
    "amazon/nova-lite-v1",
]
COMMITTEE_STARTERS = 4

# OpenRouter pass-through pricing (USD per 1M tokens) as of 2026-06-15.
# Substitutes use best-effort estimates; DEFAULT_PRICE is the fallback.
PRICE_TABLE = {
    "anthropic/claude-opus-4.8": {"input": 5.0, "output": 25.0},
    "anthropic/claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "openai/gpt-4.1": {"input": 2.0, "output": 8.0},
    "openai/gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "openai/gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-4o-mini-2024-07-18": {"input": 0.15, "output": 0.60},
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
OUTPUT_DIR = "/kaggle/working/openrouter_pilot1_test_output"
if not os.path.exists(DATA_DIR):
    DATA_DIR = "actual_data/cleaned"
    OUTPUT_DIR = "openrouter_pilot1_test_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# State file for resume after crashes / substitutions.
STATE_PATH = os.path.join(OUTPUT_DIR, "pool_state.json")

# Global counter for balanced A-D placement; persisted in state for resume.
POSITION_COUNTER = 0

# API key
OPENROUTER_API_KEY = None

# 1. Try Kaggle Secrets (preferred).
try:
    from kaggle_secrets import UserSecretsClient
    OPENROUTER_API_KEY = UserSecretsClient().get_secret("OPENROUTER_API_KEY")
except Exception:
    pass

# 2. Fall back to environment variable (local runs).
if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 3. Fall back to a private Kaggle dataset containing the key.
if not OPENROUTER_API_KEY:
    for key_path in [
        "/kaggle/input/openrouter-key-mcq/OPENROUTER_API_KEY.txt",
        "/kaggle/input/openrouter-api-key/OPENROUTER_API_KEY.txt",
    ]:
        try:
            if os.path.exists(key_path):
                with open(key_path, encoding="utf-8") as f:
                    OPENROUTER_API_KEY = f.read().strip()
                if OPENROUTER_API_KEY:
                    break
        except Exception:
            pass

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found. Add it to Kaggle Secrets, attach the private "
        "openrouter-key-mcq dataset, or set it as an environment variable."
    )

# ── Prompt variants ─────────────────────────────────────────────────────────

def load_prompt_variants():
    here = Path(__file__).resolve().parent
    candidate_paths = [
        "/kaggle/input/proverbgap-prompts/pilot1_prompt_variants.json",
        "/kaggle/input/proverbgap-data/pilot1_prompt_variants.json",
        "pilot1_prompt_variants.json",
        str(here / "pilot1_prompt_variants.json"),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            print(f"Loaded prompt variants from {path}")
            return data["prompt_variants"]
    raise FileNotFoundError(
        "pilot1_prompt_variants.json not found. Upload it to Kaggle input or place it in the working directory."
    )

PROMPT_VARIANTS = load_prompt_variants()

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

# Global cost tracker; may be rehydrated from saved state in main().
cost_tracker = CostTracker(COST_CAP_USD)


# ── Model pool (football-style substitutions) ───────────────────────────────

class ModelPool:
    """
    Manage an ordered roster of models. The first `active_limit` models are
    starters; the remainder are substitutes. Repeated failures (weighted) bench
    a model and promote the next available substitute.
    """

    def __init__(self, pool, active_limit, name, fail_threshold=2, soft_fail_threshold=5, state=None):
        self.name = name
        self.pool = list(pool)
        self.fail_threshold = fail_threshold
        self.soft_fail_threshold = soft_fail_threshold
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
        """Increment failure count for an active model and bench if threshold reached.

        Hard failures (weight >= 2) use the strict fail_threshold. Soft failures
        (weight == 1, e.g. parse/meta/idiom/leak sanitization) use a higher
        soft_fail_threshold so a high-quality generator is not benched for the
        occasional quality-filter miss.
        """
        if model not in self.active:
            return None
        self.failure_counts[model] = self.failure_counts.get(model, 0) + weight
        threshold = self.fail_threshold if weight >= 2 else self.soft_fail_threshold
        if self.failure_counts[model] >= threshold:
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
            safe_print(f"[POOL] {self.name} SUBSTITUTION: {model} -> None (no substitute available; {reason})")
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
        """JSON-serializable snapshot of pool state."""
        return {
            "name": self.name,
            "pool": self.pool,
            "active": self.active,
            "benched": self.benched,
            "failure_counts": self.failure_counts,
            "substitutions": self.substitutions,
            "fail_threshold": self.fail_threshold,
            "soft_fail_threshold": self.soft_fail_threshold,
        }


# Global pools; rehydrated from saved state in main() if available.
generator_pool = ModelPool(GENERATOR_POOL, GENERATOR_STARTERS, "GENERATOR")
committee_pool = ModelPool(COMMITTEE_POOL, COMMITTEE_STARTERS, "COMMITTEE")


# ── Cross-platform safe printing ────────────────────────────────────────────

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            text = " ".join(str(a) for a in args)
            print(text.encode("ascii", "ignore").decode("ascii"), **kwargs)
        except Exception:
            pass

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
    """Cheap probe: ask the model to echo a single letter.

    Catches routing/API/empty-content issues for ~$0.0001 per model before the
    more expensive real-generation preflight starts.
    """
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

def load_data():
    paths = {
        "English": os.path.join(DATA_DIR, "English_cleaned.csv"),
        "Arabic": os.path.join(DATA_DIR, "Arabic_cleaned.csv"),
        "Yoruba": os.path.join(DATA_DIR, "Yoruba_cleaned.csv"),
    }
    records = []
    for lang, path in paths.items():
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

def openrouter_chat(model, messages, max_tokens=None, response_format=None, retries=3, temperature=None):
    """
    Call OpenRouter with retries and 400/422 fallbacks.
    Strategy order:
      1. payload with max_tokens (if provided) + response_format (if provided)
      2. payload without max_tokens + response_format
      3. payload with max_tokens but no response_format
      4. payload without either
    This lets us survive providers that reject max_tokens or structured formats.
    """
    if temperature is None:
        temperature = TEMPERATURE
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://www.kaggle.com/",
        "X-Title": "ProverbGap Pilot 1 TEST",
    }

    def _token_limit_kwargs(model, max_tokens):
        """Use max_completion_tokens for OpenAI reasoning families.

        GPT-5 / o-series bill internal reasoning tokens against the output
        budget; max_tokens can silently truncate the visible answer. Other
        providers use the standard max_tokens parameter.
        """
        if model.startswith(("openai/gpt-5", "openai/o1", "openai/o3", "openai/o4")):
            return {"max_completion_tokens": max_tokens if max_tokens is not None else 4096}
        if max_tokens is not None:
            return {"max_tokens": max_tokens}
        return {}

    def make_payload(include_max, include_format):
        p = {"model": model, "messages": messages, "temperature": temperature}
        if include_max and max_tokens is not None:
            p.update(_token_limit_kwargs(model, max_tokens))
        if include_format and response_format is not None:
            p["response_format"] = response_format
        return p

    strategies = []
    strategies.append(make_payload(include_max=True, include_format=True))
    strategies.append(make_payload(include_max=False, include_format=True))
    strategies.append(make_payload(include_max=True, include_format=False))
    strategies.append(make_payload(include_max=False, include_format=False))
    # Remove duplicate strategies (e.g., when response_format is None)
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
                # 400/422 -> try next strategy immediately
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


# ── JSON parsing ────────────────────────────────────────────────────────────

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
    # Discard any trailing "INVALID JSON" marker and everything after it
    text = re.split(r"\*\*INVALID JSON\*\*", text, maxsplit=1)[0]
    # Prefer JSON inside a markdown code fence
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()
    # Otherwise extract the first balanced array or object
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

    # 1. Direct JSON array or object
    opts = None
    for candidate in (cleaned, cleaned.strip().strip(",").strip(), cleaned.replace("'", '"')):
        try:
            opts = json.loads(candidate)
            break
        except Exception:
            continue

    if isinstance(opts, list) and len(opts) >= 4 and all(isinstance(o, str) for o in opts):
        return [o.strip() for o in opts[:4]]

    # 2. JSON object with an array field or numeric/any string keys
    if isinstance(opts, dict):
        # Known array keys first
        for key in ("options", "choices", "distractors", "answers", "items", "result"):
            arr = opts.get(key)
            if isinstance(arr, list) and len(arr) == 4 and all(isinstance(o, str) for o in arr):
                return [o.strip() for o in arr]
        # Object with exactly 4 string values (e.g., {"0":"...", "1":"...", ...})
        str_vals = [v for v in opts.values() if isinstance(v, str)]
        if len(str_vals) == 4:
            return [v.strip() for v in str_vals]
        # Numeric keys: sort by int(key) and return values
        try:
            numeric_items = [(int(k), v) for k, v in opts.items() if isinstance(v, str) and str(k).lstrip("-").isdigit()]
            if len(numeric_items) == 4:
                numeric_items.sort(key=lambda x: x[0])
                return [v.strip() for _, v in numeric_items]
        except Exception:
            pass

    # 3. Extract quoted strings from the raw/cleaned text (handles mixed quotes)
    quoted_strings = re.findall(r"['\"](.*?)['\"]", cleaned, re.DOTALL)
    # Filter out short/meta tokens and numeric keys
    filtered = [s for s in quoted_strings if len(s.strip()) > 5 and s.strip().lower() not in {
        "options", "choices", "distractors", "answers", "items", "result", "error"
    }]
    if len(filtered) >= 4:
        return [s.strip() for s in filtered[:4]]

    # 4. Plain text lines: strip bullets/numbers and take first 4 non-empty lines
    lines = []
    for ln in (text or "").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        # Remove common leading markers
        ln = re.sub(r"^(\s*[-*•]\s+|\s*\d+[.):\]]\s+|\s*\([a-dA-D]\)\s+|\s*[a-dA-D][.):\]]\s+)", "", ln)
        # Remove surrounding quotes
        ln = ln.strip('"').strip("'")
        if ln:
            lines.append(ln)
    if len(lines) >= 4:
        return lines[:4]

    return None


# ── Validation & fallback ───────────────────────────────────────────────────

def jaccard(a, b):
    """Token-overlap similarity; 0 = distinct, 1 = identical."""
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _median_length(opts):
    """Median character length of a list of option strings."""
    lengths = [len(str(o)) for o in opts]
    return int(np.median(lengths)) if lengths else 0


def passes_length_check(candidate, reference, threshold=LENGTH_CHECK_THRESHOLD, relaxed_threshold=None):
    """Character-count parity against a reference length (or median of a list).

    Word counts are fragile for Arabic/Yoruba, so we use characters. When
    `reference` is a list of options, the median length is used so the correct
    meaning is not treated as the sole reference and distractors are checked
    against the overall scale of the four options.

    If `relaxed_threshold` is set and every option in `reference` is within that
    fraction of the shortest/longest option, the candidate is accepted regardless
    of the median check. This avoids rejecting balanced option sets where one
    option happens to be just outside the strict ±threshold window.
    """
    if isinstance(reference, (list, tuple)):
        lengths = [len(str(o)) for o in reference]
        if relaxed_threshold is not None and lengths:
            mn, mx = min(lengths), max(lengths)
            if mn > 0 and (mx - mn) / mn <= relaxed_threshold:
                return True, "all_within_relaxed"
        ref_len = _median_length(reference)
    else:
        ref_len = len(str(reference))
    cand_len = len(str(candidate))
    if ref_len > 0 and abs(cand_len - ref_len) / ref_len <= threshold:
        return True, "length"
    return False, f"length_ratio={cand_len / max(ref_len, 1):.2f}"


def negative_sample(reference_meaning, all_meanings, rng, n=3):
    others = [m for m in all_meanings if m != reference_meaning]
    if len(others) < n:
        others = others * (n // max(len(others), 1) + 1)
    rng.shuffle(others)
    return others[:n]


def _is_offensive_or_inappropriate(text):
    """Reject corpus fallbacks that contain vulgar, sexual, or offensive content."""
    lowered = str(text).lower()
    for word in _FALLBACK_OFFENSIVE_BLOCKLIST:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            return True
    return False


def _is_clean_meaning(text, reference_meaning=""):
    """Reject broken, low-quality, or too-similar fallback meanings."""
    text = str(text).strip()
    ref = str(reference_meaning).strip()
    if len(text) < 12:
        return False
    if len(text) > 300:
        return False
    # Reject extreme length outliers relative to the reference meaning.
    if ref and len(text) > 2 * len(ref):
        return False
    # Require sentence-like start.
    if not text[0].isupper():
        return False
    # Reject multiple sentences or fragments.
    if text.count('.') > 2:
        return False
    # Reject suspicious fragments that often appear in corrupted data.
    if re.search(r"\bin\s+[a-z]+\s+[a-z]+(?:\s+[a-z]+){0,3}\s+(?:resulted|caused|led| nail| insignificant)", text, flags=re.IGNORECASE):
        return False
    # Avoid meanings that are almost identical to the reference (token overlap > 50%).
    if jaccard(reference_meaning, text) > 0.5:
        return False
    return True


def _keyword_overlap_score(a, b):
    """Count content-word overlap between two strings."""
    stop = {
        "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "it", "its", "this", "that",
        "his", "her", "their", "one", "some", "any", "all", "will", "would", "could", "should", "may", "might",
        "do", "does", "did", "have", "has", "had", "not", "no", "than", "more", "most", "much", "many",
        "who", "which", "when", "where", "what", "how", "why", "can", "cannot"
    }
    ta = set(re.findall(r"[a-zA-Z']+", str(a).lower())) - stop
    tb = set(re.findall(r"[a-zA-Z']+", str(b).lower())) - stop
    if not ta or not tb:
        return 0
    return len(ta & tb)


def _length_ratio_ok(m, reference_meaning, lo=0.5, hi=1.5):
    """Return True if candidate length is within [lo, hi] of the reference length."""
    if not reference_meaning:
        return True
    ref_len = len(str(reference_meaning).strip())
    if ref_len == 0:
        return True
    cand_len = len(str(m).strip())
    ratio = cand_len / ref_len
    return lo <= ratio <= hi


def semantically_distinct_negative_sample(reference_meaning, all_meanings, rng, n=1, max_jaccard=0.5, language=None, df_all=None, exclude=None, use_llm=True):
    """
    Return n fallback distractors that are not identical to the reference,
    have low token overlap with it, pass basic quality filters, and are length-matched.
    Prefer same-language meanings that share some topical keywords with the reference.
    `exclude` is an optional set/list of strings to avoid (normalized before comparison).

    When `use_llm` is True and n == 1 and a proverb context is available, the function
    first tries a cheap LLM call to generate a proverb-specific hard negative before
    falling back to the corpus sampler.
    """
    # v67 — single-distractor replacements can optionally use the cheap LLM hard-negative
    # generator. Disabled by default in the frozen v67 config so the main run uses the
    # stable corpus sampler; enable USE_LLM_FALLBACK for the ablation study.
    if USE_LLM_FALLBACK and use_llm and n == 1 and _LLM_FALLBACK_PROVERB and OPENROUTER_API_KEY:
        try:
            candidate = generate_llm_fallback_distractor(
                reference_meaning, all_meanings, rng, language=language, exclude=exclude
            )
            if candidate and str(candidate).strip():
                return [candidate]
        except Exception as e:
            safe_print(f"  [LLM FALLBACK] sampler dispatch failed: {e}")
    exclude_norm = {_normalized_option(x) for x in (exclude or [])}

    def is_acceptable(m):
        if m == reference_meaning:
            return False
        if jaccard(reference_meaning, m) > max_jaccard:
            return False
        if has_generic_english_idiom([m]):
            return False
        if _is_offensive_or_inappropriate(m):
            return False
        if _normalized_option(m) in exclude_norm:
            return False
        return True

    def length_filter(candidates, lo, hi):
        return [m for m in candidates if _length_ratio_ok(m, reference_meaning, lo=lo, hi=hi)]

    def build_pool(candidates):
        pool = [m for m in candidates if is_acceptable(m)]
        # Try strict length match first, then relax.
        length_pool = length_filter(pool, 0.5, 1.5)
        if len(length_pool) < n:
            length_pool = length_filter(pool, 0.3, 2.0)
        if len(length_pool) < n:
            length_pool = pool
        # Weight candidates by keyword overlap with the reference.
        scored = [(m, max(_keyword_overlap_score(reference_meaning, m), 0.0)) for m in length_pool]
        return scored

    def _weighted_sample(scored, k):
        """Sample up to k items without replacement using score weights."""
        pool = list(scored)
        out = []
        while pool and len(out) < k:
            weights = [max(s, 0.0) + 0.05 for _, s in pool]
            total = sum(weights)
            probs = [w / total for w in weights]
            idx = rng.choices(range(len(pool)), weights=probs, k=1)[0]
            out.append(pool.pop(idx)[0])
        return out

    candidates = []
    if df_all is not None and language is not None:
        same_lang = df_all[df_all["language"] == language]["meaning"].tolist()
        candidates = build_pool(same_lang)
    if len(candidates) < n:
        candidates = build_pool(list(all_meanings))

    # Randomize order weighted by topical overlap so repeated calls do not
    # always collide on the same top candidate.
    candidate_order = _weighted_sample(candidates, len(candidates))

    selected = []
    def _is_near_duplicate(m):
        m_norm = _normalized_option(m)
        if m_norm in exclude_norm:
            return True
        for s in selected + [reference_meaning]:
            if m_norm == _normalized_option(s):
                return True
            if jaccard(m, s) > max_jaccard:
                return True
        return False

    # First pass: require clean quality.
    for m in candidate_order:
        if _is_clean_meaning(m, reference_meaning) and not _is_near_duplicate(m):
            selected.append(m)
        if len(selected) == n:
            return selected
    # Second pass: relax strict quality but still require sentence-like text,
    # blocklist, length ratio, and token overlap control.
    for m in candidate_order:
        if m in selected:
            continue
        m_stripped = str(m).strip()
        if len(m_stripped) < 12 or not m_stripped[0].isupper():
            continue
        if reference_meaning and len(m_stripped) > 2 * len(str(reference_meaning).strip()):
            continue
        if has_generic_english_idiom([m_stripped]):
            continue
        if _is_offensive_or_inappropriate(m_stripped):
            continue
        if not _is_near_duplicate(m):
            selected.append(m)
        if len(selected) == n:
            return selected
    # Final fallback: use any remaining candidate not excluded/near-duplicate/offensive.
    remaining = [m for m in candidate_order if m not in selected
                 and _normalized_option(m) != _normalized_option(reference_meaning)
                 and _normalized_option(m) not in exclude_norm
                 and not _is_offensive_or_inappropriate(m)
                 and not _is_near_duplicate(m)]
    for m in remaining:
        selected.append(m)
        if len(selected) == n:
            return selected
    # Backup: draw from the full meaning pool, ignoring keyword scores but
    # still avoiding exact duplicates and excluded items.
    backup = []
    if all_meanings:
        backup.extend(list(all_meanings))
    if df_all is not None and language is not None:
        backup.extend(df_all[df_all["language"] == language]["meaning"].tolist())
    rng.shuffle(backup)
    for m in backup:
        if (_normalized_option(m) != _normalized_option(reference_meaning)
                and _normalized_option(m) not in exclude_norm
                and not _is_offensive_or_inappropriate(m)
                and not _is_near_duplicate(m)):
            selected.append(m)
        if len(selected) == n:
            return selected
    # Generic last-resort distractors (rarely used).
    generics = [
        "It conveys a different moral lesson.",
        "It refers to an unrelated situation.",
        "The meaning is the opposite of the proverb.",
        "It describes a common proverbial theme.",
    ]
    rng.shuffle(generics)
    for m in generics:
        if not _is_near_duplicate(m):
            selected.append(m)
        if len(selected) == n:
            return selected
    # Absolute last resort (should never happen).
    while len(selected) < n:
        selected.append(reference_meaning + " (fallback)")
    return selected[:n]


RAW_OUTPUTS = []


def _make_generation_fallback(meaning, all_meanings, rng, language, df_all):
    """Return fallback 4-option list when a generator call fails."""
    # Try up to 5 times to obtain distractors inside the semantic band.
    for attempt in range(5):
        distractors = semantically_distinct_negative_sample(
            meaning, all_meanings, rng, n=3, language=language, df_all=df_all
        )
        opts = [meaning] + distractors
        # Remove any obvious generic idioms or correct-meaning leaks.
        if has_generic_english_idiom(opts):
            rng.shuffle(all_meanings)
            continue
        if has_correct_meaning_leak(opts):
            rng.shuffle(all_meanings)
            continue
        # Repair duplicates if the sampler produced them.
        opts, _ = repair_duplicate_options(opts, all_meanings, rng, language=language, df_all=df_all)
        sem_ok, _ = semantic_distance_ok(opts, language)
        if sem_ok:
            return opts
        rng.shuffle(all_meanings)
    return opts


# Cache for gold-meaning curation so the same proverb is only rewritten once per
# run even if it is generated by multiple generators/variants.
_GOLD_MEANING_CACHE = {}


def curate_gold_meaning(proverb, meaning, language, rng, model=GOLD_CURATION_MODEL):
    """Rewrite a literal/awkward gloss into natural English for any language."""
    key = (str(proverb).strip().lower(), str(language or "").lower(), str(meaning).strip().lower())
    if key in _GOLD_MEANING_CACHE:
        return _GOLD_MEANING_CACHE[key]

    if not OPENROUTER_API_KEY:
        _GOLD_MEANING_CACHE[key] = meaning
        return meaning

    prompt_tokens_est = 120
    output_tokens_est = 80
    if cost_tracker.would_exceed(model, prompt_tokens_est, output_tokens_est):
        safe_print(f"  [GOLD CURATION] skipped: would exceed cost cap")
        _GOLD_MEANING_CACHE[key] = meaning
        return meaning

    lang_note = ""
    if language and language.lower() == "yoruba":
        lang_note = (
            " This is a Yoruba proverb. Keep the concrete image of a neckless or "
            "collarless gourd (calabash), the farmer, and the act of tying or binding it."
        )
    elif language and language.lower() == "arabic":
        lang_note = (
            " This is an Arabic proverb. Preserve the specific moral or social "
            "situation; do not reduce it to a generic English idiom or proverb."
        )

    prompt = (
        "Rewrite the following English gloss of a proverb into ONE clear, natural "
        "English sentence that preserves the original cultural meaning. "
        "Do NOT use a well-known English idiom or proverb as the rewritten meaning. "
        "Keep roughly the same length. Do NOT explain. Output ONLY the rewritten sentence."
        f"{lang_note}\n\n"
        f"Proverb: {proverb}\n"
        f"Gloss: {meaning}\n\n"
        "Rewritten meaning:"
    )
    try:
        resp = openrouter_chat(model, [{"role": "user", "content": prompt}], max_tokens=256)
        text = extract_text(resp)
        text = text.strip().strip('"').strip("'")
        prompt_tok, out_tok = extract_usage(resp)
        cost_tracker.add(model, prompt_tok or prompt_tokens_est, out_tok or output_tokens_est, "gold_curation")
        if text and len(text) >= 12 and text[0].isupper() and text.count(".") <= 2:
            safe_print(f"  [GOLD CURATION {language}] rewritten: {meaning!r} -> {text!r}")
            _GOLD_MEANING_CACHE[key] = text
            return text
    except Exception as e:
        safe_print(f"  [GOLD CURATION {language}] FAILED: {e}")

    _GOLD_MEANING_CACHE[key] = meaning
    return meaning


def generate_options(proverb, meaning, language, variant, rng, all_meanings, df_all, generator_model):
    """
    Generate 4 options using a specific prompt variant and generator model.

    Returns (options, meta). meta contains:
      - status: "generated", "partial", "length_fallback", "parse_fallback", or "hard_fallback"
      - fallback_count: number of distractors replaced by length fallback (if any)
      - failure_weight: 2 for hard failures (API/empty/truncation), 1 for parse failures,
                        0 for successful generation.
    """
    cost_tracker.check()
    nli_replaced = 0
    leak_replaced = 0

    # v64 — rewrite literal/awkward glosses into natural English before asking
    # generators/auditors to work with them. Apply to all languages; Arabic and
    # Yoruba dataset glosses are especially literal/idiomatic.
    original_meaning = meaning
    # v69 — make the LLM fallback generator proverb-aware so it can produce
    # culturally specific hard negatives instead of generic corpus samples.
    _set_llm_fallback_context(proverb, variant["name"])
    if USE_GOLD_MEANING_CURATION:
        meaning = curate_gold_meaning(proverb, meaning, language, rng)

    system_prompt = variant["system_prompt"]
    user_prompt = variant["user_prompt_template"].format(
        proverb=proverb, language=language, correct_meaning=meaning
    )
    # Yoruba-specific hardening: add cultural-context reminder and ban generic
    # English idioms that have repeatedly leaked into Yoruba distractors.
    if language and language.lower() == "yoruba":
        user_prompt += (
            "\n\nCRITICAL cultural-context instruction: This is a Yoruba proverb. "
            "Every option must read like a plausible interpretation of a Yoruba proverb, "
            "grounded in Yoruba cultural logic (community, elders, divination, gender roles, "
            "proverbs about social order, etc.). "
            "Do NOT use generic English idioms or proverbs (e.g., 'a bird in the hand', "
            "'the apple does not fall far from the tree', 'in unity there is strength', "
            "'a man is known by the company he keeps', 'roll with the punches') "
            "unless they are semantically tied to this specific Yoruba meaning. "
            "Distractors must be plausible misinterpretations within a Yoruba cultural frame, "
            "not literal English translations of a generic saying. "
            "If the correct meaning is itself a literal translation, paraphrase it into "
            "natural English while preserving the Yoruba cultural sense; distractors should "
            "be alternative Yoruba-style interpretations, not unrelated English proverbs."
        )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    prompt_tokens_est = sum(len(m["content"].split()) for m in messages) + 50
    output_tokens_est = 200

    if cost_tracker.would_exceed(generator_model, prompt_tokens_est, output_tokens_est):
        # Treat a cost-cap skip as a hard failure so the pool can substitute.
        opts = _make_generation_fallback(meaning, all_meanings, rng, language, df_all)
        status_meta = {
            "status": "hard_fallback",
            "error": f"Call would exceed ${COST_CAP_USD:.2f} cap (spent ${cost_tracker.spent:.4f}).",
            "fallback_count": 0,
            "failure_weight": 2,
        }
        safe_print(f"  [HARD_FALLBACK] {generator_model}/{variant['name']}: {status_meta['error']}")
        RAW_OUTPUTS.append({
            "stage": "generation",
            "generator_model": generator_model,
            "variant": variant["name"],
            "language": language,
            "proverb": proverb,
            "correct_meaning": meaning,
            "raw_model_output": "",
            "finish_reason": None,
            "status": status_meta["status"],
            "error": status_meta["error"],
        })
        _clear_llm_fallback_context()
        return opts, status_meta

    raw_text = None
    finish_reason = None
    opts = None
    last_error = None
    for attempt in range(2):
        try:
            resp = openrouter_chat(generator_model, messages, max_tokens=MAX_TOKENS_GEN, response_format=None)
            text = extract_text(resp)
            raw_text = text
            finish_reason = extract_finish_reason(resp)
            prompt_tok, out_tok = extract_usage(resp)
            cost_tracker.add(generator_model, prompt_tok or prompt_tokens_est, out_tok, f"generation-{generator_model}-{variant['name']}")

            if not text or not text.strip():
                raise ValueError("Empty response content")
            if finish_reason == "length":
                raise ValueError(f"Truncated response (finish_reason=length)")
            opts = parse_options(text)
            if opts is None:
                raise ValueError(
                    f"Could not parse JSON options. finish_reason={finish_reason}. "
                    f"Raw text: {repr(text)[:500]}. Response snippet: {response_snippet(resp, 1000)}"
                )
            if has_meta_text(opts):
                raise ValueError(
                    f"Parsed options contain meta-text / markdown. opts={opts!r}"
                )
            # Replace any distractor that contains a generic English idiom. The correct
            # option is allowed to be a well-known English idiom (e.g., "Charity begins at home").
            opts, blocklist_replaced = _sanitize_blocked_idioms(
                opts, meaning, all_meanings, rng, language=language, df_all=df_all
            )
            # Replace any distractor that echoes or near-paraphrases the correct meaning.
            leak_threshold = LEAK_THRESHOLD_BY_LANGUAGE.get(
                (language or "").lower(), LEAK_THRESHOLD_BY_LANGUAGE["default"]
            )
            opts, leak_replaced = _sanitize_correct_meaning_leak(
                opts, all_meanings, rng, language=language, df_all=df_all, threshold=leak_threshold
            )
            # Replace any distractor that is too similar/dissimilar to the correct meaning.
            opts, sem_replaced = _sanitize_semantic_distance(
                opts, language, all_meanings, df_all, rng
            )
            break  # success
        except Exception as e:
            last_error = e
            # Classify failures: hard = API/empty/truncation; soft = parse/meta/idiom.
            is_hard = (
                finish_reason == "length"
                or raw_text is None
                or not str(raw_text).strip()
            )
            if attempt == 0 and not is_hard:
                safe_print(
                    f"  [RETRY] {generator_model}/{variant['name']}: {e}"
                )
                continue
            weight = 2 if is_hard else 1
            status = "hard_fallback" if is_hard else "parse_fallback"
            opts = _make_generation_fallback(meaning, all_meanings, rng, language, df_all)
            status_meta = {
                "status": status,
                "error": str(e),
                "fallback_count": 0,
                "nli_replaced": 0,
                "failure_weight": weight,
            }
            safe_print(
                f"  [{status.upper()}] {generator_model}/{variant['name']}: {e}\n"
                f"                   raw_text={repr(raw_text)[:400]} finish_reason={finish_reason}"
            )
            RAW_OUTPUTS.append({
                "stage": "generation",
                "generator_model": generator_model,
                "variant": variant["name"],
                "language": language,
                "proverb": proverb,
                "correct_meaning": meaning,
                "raw_model_output": raw_text or "",
                "finish_reason": finish_reason,
                "status": status_meta["status"],
                "error": status_meta["error"],
            })
            _clear_llm_fallback_context()
            return opts, status_meta

    if opts is None:
        # Should not happen, but guard anyway.
        opts = _make_generation_fallback(meaning, all_meanings, rng, language, df_all)
        _clear_llm_fallback_context()
        return opts, {"status": "parse_fallback", "error": str(last_error), "fallback_count": 0, "nli_replaced": 0, "failure_weight": 1}

    # Replace any distractor that NLI flags as entailing/entailed by the correct meaning.
    if USE_NLI_FILTER:
        opts, nli_replaced = _sanitize_nli_paraphrases(
            opts, language, all_meanings, df_all, rng
        )
    else:
        nli_replaced = 0

    # Validate option lengths against the median length of all four options so
    # the correct meaning is not the only reference and outliers are replaced.
    # If the whole set is within LENGTH_RELAXED_THRESHOLD, accept it as-is.
    validated = [opts[0]]
    length_replaced = 0
    correct_length_outlier = 0
    used_fallbacks = {str(opts[0]).strip().lower()}
    for d in opts[1:]:
        ok, reason = passes_length_check(d, opts, relaxed_threshold=LENGTH_RELAXED_THRESHOLD)
        if ok:
            validated.append(d)
        else:
            length_replaced += 1
            alt = semantically_distinct_negative_sample(
                opts[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=used_fallbacks
            )[0]
            validated.append(alt)
            used_fallbacks.add(str(alt).strip().lower())
    # Flag a correct meaning that is itself a length outlier, but do not count it
    # toward fallback/partial status -- only distractor parity affects difficulty.
    ok0, _ = passes_length_check(opts[0], opts, relaxed_threshold=LENGTH_RELAXED_THRESHOLD)
    if not ok0:
        correct_length_outlier = 1

    # Count distractor replacements (length, leak, semantic, NLI) toward
    # fallback/partial status. Blocklist and duplicate repairs are intentionally
    # excluded: they are policy-level cleanups, not generation failures.
    fallback_count = length_replaced + leak_replaced + sem_replaced + nli_replaced

    # Repair any duplicate or near-duplicate options introduced by sanitization or length fallback.
    validated, dup_replaced = repair_duplicate_options(
        validated, all_meanings, rng, language=language, df_all=df_all
    )

    if fallback_count == 0:
        status = "generated"
    elif length_replaced >= 2:
        status = "length_fallback"
    elif fallback_count < 3:
        status = "partial"
    else:
        status = "length_fallback"
    status_meta = {
        "status": status,
        "fallback_count": fallback_count,
        "length_replaced": length_replaced,
        "correct_length_outlier": correct_length_outlier,
        "blocklist_replaced": blocklist_replaced,
        "dup_replaced": dup_replaced,
        "nli_replaced": nli_replaced,
        "leak_replaced": leak_replaced,
        "failure_weight": 0,
    }

    RAW_OUTPUTS.append({
        "stage": "generation",
        "generator_model": generator_model,
        "variant": variant["name"],
        "language": language,
        "proverb": proverb,
        "correct_meaning": meaning,
        "original_meaning": original_meaning if original_meaning != meaning else "",
        "curated_meaning": meaning if original_meaning != meaning else "",
        "raw_model_output": raw_text or "",
        "finish_reason": finish_reason,
        "status": status_meta["status"],
        "fallback_count": status_meta.get("fallback_count", 0),
        "length_replaced": status_meta.get("length_replaced", 0),
        "correct_length_outlier": status_meta.get("correct_length_outlier", 0),
        "blocklist_replaced": status_meta.get("blocklist_replaced", 0),
        "dup_replaced": status_meta.get("dup_replaced", 0),
    })

    # ── Self-critique loop ──────────────────────────────────────────────────
    # Ask a frozen critic to audit the options. If the critic finds the correct
    # answer too easily, ask the generator to rewrite the distractors once.
    if USE_SELF_CRITIQUE and MAX_SELF_CRITIQUE_ROUNDS > 0 and status_meta["status"] not in ("hard_fallback", "parse_fallback"):
        validated, status_meta = _self_critique_loop(
            proverb, meaning, language, variant, generator_model,
            validated, status_meta, all_meanings, df_all, rng
        )

    _clear_llm_fallback_context()
    return validated, status_meta


# ── Self-critique helpers ───────────────────────────────────────────────────

def _options_dict_for_critique(opts, correct_pos=0):
    """Build a temporary A-D dict for the critic without consuming the global position counter."""
    distractors = opts[1:]
    ordered = distractors[:correct_pos] + [opts[0]] + distractors[correct_pos:]
    labels = ["A", "B", "C", "D"]
    return {labels[i]: ordered[i] for i in range(4)}, labels[correct_pos]


def _critic_pick(options_dict, critic_model, prompt_tokens_est=80):
    """Run a frozen critic model on the four options and return A-D vote or None."""
    if not critic_model or not USE_SELF_CRITIQUE:
        return None
    text = "\n".join([f"{k}. {v}" for k, v in options_dict.items()])
    messages = [
        {"role": "system", "content": "You are a strict multiple-choice critic. Reply ONLY with the single letter A, B, C, or D. Do not explain."},
        {"role": "user", "content": f"Which option is correct?\n\n{text}"},
    ]
    try:
        if cost_tracker.would_exceed(critic_model, prompt_tokens_est, MAX_TOKENS_AUDIT):
            return None
        resp = openrouter_chat(critic_model, messages, max_tokens=MAX_TOKENS_AUDIT)
        vote_text = extract_text(resp)
        prompt_tok, out_tok = extract_usage(resp)
        cost_tracker.add(critic_model, prompt_tok or prompt_tokens_est, out_tok, "self_critique")
        return extract_choice(vote_text)
    except Exception as e:
        safe_print(f"  [SELF-CRITIQUE] critic {critic_model} failed: {e}")
        return None


def _rewrite_with_critique(proverb, meaning, language, variant, generator_model,
                           options_dict, correct_label, all_meanings, df_all, rng):
    """Ask the generator to rewrite distractors after a critic identified the correct answer."""
    cost_tracker.check()
    options_text = "\n".join([f"{k}. {v}" for k, v in options_dict.items()])
    system_prompt = variant["system_prompt"]
    user_prompt = (
        f"Proverb ({language}): {proverb}\n"
        f"Correct meaning: {meaning}\n\n"
        f"I generated these options, but a critic correctly chose {correct_label}.\n"
        f"{options_text}\n\n"
        "Rewrite the distractors so the correct answer is no longer obvious from the options alone. "
        "Keep the same correct meaning at index 0. Make the three distractors more tempting, "
        "but still wrong for this proverb. All four options must be within ±20% character count, "
        "share the same register, and avoid negations/antonyms. Return ONLY a JSON array of 4 strings."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    prompt_tokens_est = sum(len(m["content"].split()) for m in messages) + 50
    output_tokens_est = 200
    if cost_tracker.would_exceed(generator_model, prompt_tokens_est, output_tokens_est):
        return None, {"status": "critique_skipped", "error": "cost cap", "fallback_count": 0, "failure_weight": 0}
    try:
        resp = openrouter_chat(generator_model, messages, max_tokens=MAX_TOKENS_GEN)
        text = extract_text(resp)
        prompt_tok, out_tok = extract_usage(resp)
        cost_tracker.add(generator_model, prompt_tok or prompt_tokens_est, out_tok, f"generation-critique-{generator_model}-{variant['name']}")
        if not text or not text.strip():
            raise ValueError("Empty critique rewrite response")
        new_opts = parse_options(text)
        if new_opts is None:
            raise ValueError(f"Could not parse critique rewrite. Raw text: {repr(text)[:400]}")
        if has_meta_text(new_opts):
            raise ValueError(f"Critique rewrite contains meta-text / markdown. opts={new_opts!r}")
        # Validate lengths and replace outliers.
        validated = [new_opts[0]]
        fallback_count = 0
        for d in new_opts[1:]:
            ok, _ = passes_length_check(d, new_opts, relaxed_threshold=LENGTH_RELAXED_THRESHOLD)
            if ok:
                validated.append(d)
            else:
                fallback_count += 1
                alt = semantically_distinct_negative_sample(new_opts[0], all_meanings, rng, n=1, language=language, df_all=df_all)[0]
                validated.append(alt)
        # Correct-option length outlier is reported but not counted as a fallback.
        ok0, _ = passes_length_check(new_opts[0], new_opts, relaxed_threshold=LENGTH_RELAXED_THRESHOLD)
        correct_length_outlier = 0 if ok0 else 1
        status = "generated" if fallback_count == 0 else ("partial" if fallback_count < 3 else "length_fallback")
        RAW_OUTPUTS.append({
            "stage": "generation",
            "generator_model": generator_model,
            "variant": variant["name"],
            "language": language,
            "proverb": proverb,
            "correct_meaning": meaning,
            "raw_model_output": text or "",
            "finish_reason": None,
            "status": status,
            "fallback_count": fallback_count,
            "correct_length_outlier": correct_length_outlier,
            "critique_rewrite": True,
        })
        return validated, {"status": status, "fallback_count": fallback_count, "failure_weight": 0}
    except Exception as e:
        safe_print(f"  [SELF-CRITIQUE] rewrite failed for {generator_model}/{variant['name']}: {e}")
        return None, {"status": "critique_failed", "error": str(e), "fallback_count": 0, "failure_weight": 0}


def _self_critique_loop(proverb, meaning, language, variant, generator_model,
                        opts, meta, all_meanings, df_all, rng):
    """Run at most MAX_SELF_CRITIQUE_ROUNDS critic/rewrite iterations."""
    for round_idx in range(MAX_SELF_CRITIQUE_ROUNDS):
        options_dict, correct_label = _options_dict_for_critique(opts, correct_pos=0)
        critic_vote = _critic_pick(options_dict, CRITIC_MODEL)
        if critic_vote is None or critic_vote != correct_label:
            break
        safe_print(
            f"  [SELF-CRITIQUE] {generator_model}/{variant['name']}: critic picked {critic_vote} "
            f"(correct {correct_label}) — rewriting (round {round_idx + 1})"
        )
        new_opts, new_meta = _rewrite_with_critique(
            proverb, meaning, language, variant, generator_model,
            options_dict, correct_label, all_meanings, df_all, rng
        )
        if new_opts is not None and new_meta["status"] not in ("critique_skipped", "critique_failed"):
            opts = new_opts
            meta = new_meta
            meta["critique_rounds"] = round_idx + 1
        else:
            break
    return opts, meta


# ── MCQ assembly ────────────────────────────────────────────────────────────

def assemble_mcq(opts, mcq_id):
    """Place correct answer at the next position in a round-robin A-D cycle.

    A global counter ensures balanced key distribution across the run. The
    counter is persisted in state so resumed runs continue the cycle.
    """
    global POSITION_COUNTER
    labels = ["A", "B", "C", "D"]
    correct_pos = POSITION_COUNTER % 4
    POSITION_COUNTER += 1
    distractors = opts[1:]
    ordered = distractors[:correct_pos] + [opts[0]] + distractors[correct_pos:]
    return {labels[i]: ordered[i] for i in range(4)}, labels[correct_pos]


def _normalized_option(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def _token_overlap(a, b):
    """Jaccard-style token overlap between two normalized strings."""
    ta = set(_normalized_option(a).split())
    tb = set(_normalized_option(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def has_duplicate_options(options_dict, near_duplicate_threshold=0.85):
    """
    Return True if any two options are identical or near-identical.
    Near-duplicate is defined as token overlap >= near_duplicate_threshold.
    """
    values = list(options_dict.values())
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if _normalized_option(values[i]) == _normalized_option(values[j]):
                return True
            if _token_overlap(values[i], values[j]) >= near_duplicate_threshold:
                return True
    return False


def repair_duplicate_options(opts, all_meanings, rng, language=None, df_all=None, max_attempts=8):
    """
    Replace duplicate or near-duplicate options with fresh fallback distractors.
    Returns (repaired_opts, n_replaced).
    """
    if not opts or len(opts) != 4:
        return opts, 0
    repaired = list(opts)
    replaced = 0
    existing = {_normalized_option(o) for o in repaired}
    for i in range(4):
        duplicate = False
        for j in range(4):
            if i == j:
                continue
            if _normalized_option(repaired[i]) == _normalized_option(repaired[j]):
                duplicate = True
                break
            if _token_overlap(repaired[i], repaired[j]) >= 0.85:
                duplicate = True
                break
        if not duplicate:
            continue
        for _ in range(max_attempts):
            alt = semantically_distinct_negative_sample(
                repaired[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=existing
            )[0]
            alt_norm = _normalized_option(alt)
            if alt_norm and alt_norm not in existing:
                repaired[i] = alt
                existing.add(alt_norm)
                replaced += 1
                break
    return repaired, replaced


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

# Generic English proverbs / idioms that should not appear as distractors, because
# they are culturally mismatched surface shortcuts and unrelated to the target proverb.
_GENERIC_ENGLISH_IDIOM_BLOCKLIST = [
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
    # Observed leakage in Pilot 1 N=1 local run (2026-06-20)
    "just around the corner",
    "words of wisdom",
    "tell a lie",
    "no matter how close",
    "foolish inquiries",
    "chicken cannot",
    "pressed men",
    "if one is determined enough",
    "already negative situation",
    "the hand that he washed",
    "your mother did",
    "the person rubbing himself",
    "a volunteer is worth",
    "pressed men",
    "twenty pressed men",
    # Observed leakage in Pilot 1 N=2 local run (2026-06-20) — fallback / partial rows
    "a man is known by the company he keeps",
    "a pint-sized man",
    "a word to a wise man is enough",
    "you cannot teach an old dog new tricks",
    "you can't teach an old dog new tricks",
    "roll with the punches",
    "add fuel to the fire",
    "add fuel to fire",
    "a candle for god a stump for the devil",
    "one man's meat is another man's poison",
    "one mans meat is another mans poison",
    "man plans and god decides",
    "do not count your chickens before they are hatched",
    "dont count your chickens before they hatch",
    "grasp all lose all",
    # Observed leakage in Pilot 1 v58 Kaggle run (2026-06-20)
    "east or west home is best",
    "east or west home is the best",
    "go big or go home",
    "a lion at home a lamb abroad",
    "a lion at home is a lamb abroad",
    "make a rod for your own back",
    "make a rod for ones own back",
    "make a rod for one's own back",
    "defend your home",
    "charity begins with strangers",
    "charity begins only in crises",
    "charity begins when requested",
    "charity begins through obligation",
    # Observed leakage in Pilot 1 v63 Kaggle run (2026-06-21)
    "people in glass houses should not throw stones",
    "people in glass houses shouldn't throw stones",
    "the proof is in the pudding",
    "the proofs in the pudding",
    "speech is silver silence is gold",
    "silence is golden",
    "the smarter you are the less you speak",
    "opinion comes before the bravery of the braves",
    "mind your own business",
    "add fuel to the flames",
    "better suffer ill than do ill",
    "experience is the best teacher",
]


def _normalize_for_blocklist(text):
    """Normalize option text for fuzzy blocklist matching."""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_generic_english_idiom(opts, skip_correct_option=False):
    """Return True if any option is a generic English idiom/proverb unrelated to the target proverb.

    If `skip_correct_option` is True, the option at index 0 (the correct meaning) is
    allowed to contain a blocklisted phrase. This matters when the curated gold meaning
    itself is a well-known English idiom (e.g., the Arabic proverb glossed as
    "Charity begins at home").
    """
    if not opts:
        return False
    start = 1 if skip_correct_option and len(opts) > 1 else 0
    for o in opts[start:]:
        text = _normalize_for_blocklist(o)
        for blocked in _GENERIC_ENGLISH_IDIOM_BLOCKLIST:
            if _normalize_for_blocklist(blocked) in text:
                return True
    return False


def _sanitize_blocked_idioms(opts, meaning, all_meanings, rng, language=None, df_all=None, max_attempts=5):
    """Replace any distractor that contains a generic English idiom/proverb.

    The correct option (index 0) is allowed to contain the phrase. Returns
    (sanitized_options, n_replaced). Raises ValueError if a blocked distractor
    cannot be replaced after `max_attempts`.
    """
    if not opts or len(opts) != 4:
        return opts, 0
    sanitized = list(opts)
    replaced = 0
    used = {str(sanitized[0]).strip().lower(), str(meaning).strip().lower()}
    for idx in range(1, 4):
        if not has_generic_english_idiom([sanitized[idx]]):
            continue
        attempt = 0
        while attempt < max_attempts:
            alts = semantically_distinct_negative_sample(
                sanitized[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=used
            )
            if not alts:
                attempt += 1
                continue
            alt = str(alts[0]).strip()
            if not alt or has_generic_english_idiom([alt]):
                attempt += 1
                continue
            sanitized[idx] = alt
            used.add(alt.lower())
            replaced += 1
            break
        if attempt == max_attempts:
            raise ValueError(
                f"Could not replace blocklisted distractor at index {idx}: {opts[idx]!r}"
            )
    return sanitized, replaced


def has_correct_meaning_leak(opts, threshold=0.80):
    """
    Return True if any distractor is a substring/superstring, leading-phrase echo,
    or near-paraphrase of the correct meaning (index 0). This catches literal echoes
    of the gloss and variants that preserve the opening words.
    """
    if not opts or len(opts) != 4:
        return False
    correct = _normalize_for_blocklist(opts[0])
    for o in opts[1:]:
        if _is_correct_meaning_leak(o, correct, threshold):
            return True
    return False


_LEAD_STOP = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
              "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
              "it", "its", "this", "that", "and", "or"}


def _is_correct_meaning_leak(distractor, correct, threshold=0.80):
    """Return True if a single distractor is a leading-phrase echo or high token overlap of the correct meaning."""
    correct = _normalize_for_blocklist(correct)
    distractor = _normalize_for_blocklist(distractor)
    if not correct or not distractor:
        return True
    if distractor in correct or correct in distractor:
        return True
    correct_tokens = set(correct.split())
    if not correct_tokens:
        return False
    correct_words = correct.split()
    lead_phrases = []
    if len(correct_words) >= 3:
        lead_phrases.append(" ".join(correct_words[:3]))
    if len(correct_words) >= 2 and all(w not in _LEAD_STOP for w in correct_words[:2]):
        lead_phrases.append(" ".join(correct_words[:2]))
    if len(correct_words) < 2:
        lead_phrases.append(correct)
    for phrase in lead_phrases:
        if phrase and phrase in distractor:
            return True
    distractor_tokens = set(distractor.split())
    if not distractor_tokens:
        return True
    overlap = len(correct_tokens & distractor_tokens) / max(len(correct_tokens), len(distractor_tokens))
    return overlap >= threshold


def _sanitize_correct_meaning_leak(opts, all_meanings, rng, language=None, df_all=None, threshold=0.80, max_attempts=8):
    """
    Replace distractors that echo or near-paraphrase the correct meaning.
    Returns (sanitized_opts, n_replaced).
    """
    if not opts or len(opts) != 4:
        return opts, 0
    sanitized = list(opts)
    replaced = 0
    correct = str(sanitized[0]).strip()
    existing = {str(o).strip().lower() for o in sanitized}
    for idx in range(1, 4):
        attempt = 0
        while attempt < max_attempts and _is_correct_meaning_leak(sanitized[idx], correct, threshold):
            alt = semantically_distinct_negative_sample(
                sanitized[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=existing
            )[0]
            alt_stripped = str(alt).strip()
            if alt_stripped.lower() in existing or _is_correct_meaning_leak(alt_stripped, correct, threshold):
                attempt += 1
                continue
            sanitized[idx] = alt_stripped
            existing.add(alt_stripped.lower())
            replaced += 1
            break
    return sanitized, replaced


def has_meta_text(opts):
    """Return True if any option contains markdown, headings, or model instructions."""
    if not opts or len(opts) != 4:
        return True
    for o in opts:
        text = str(o).strip()
        if not text:
            return True
        for pat in _META_PATTERNS:
            if pat.search(text):
                return True
    return False


def _has_meta_text_single(text):
    """Return True if a single string contains markdown, headings, or model instructions."""
    if not text:
        return True
    text = str(text).strip()
    if not text:
        return True
    for pat in _META_PATTERNS:
        if pat.search(text):
            return True
    return False


# ── Semantic-distance filter (multilingual embeddings) ──────────────────────

# Cosine-similarity band between each distractor and the correct option.
# Distractors too similar to the correct meaning are trivial synonyms;
# distractors too dissimilar are obvious outliers or unrelated idioms.
# Yoruba meanings are sparser and more literal, so the band is slightly wider.
SEMANTIC_DISTANCE_BAND = {
    # Lower bound is intentionally lenient: distractors only need to be in the
    # same broad semantic neighbourhood as the correct meaning, not close synonyms.
    # Upper bound relaxed further in v62 per language to reduce fallback
    # replacements while still relying on the NLI paraphrase filter to catch
    # strong paraphrases.
    "default": {"min": 0.12, "max": 0.86},
    "english": {"min": 0.12, "max": 0.88},
    "yoruba": {"min": 0.10, "max": 0.90},
}


def _embedding_similarities(opts):
    """Return cosine similarities between the correct option (index 0) and each distractor."""
    model = _load_embedding_model()
    embeddings = model.encode([str(o) for o in opts], convert_to_numpy=True, show_progress_bar=False)
    # L2-normalise and compute cosine similarity.
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    embeddings = embeddings / norms
    correct = embeddings[0]
    sims = embeddings[1:].dot(correct)
    return sims


def semantic_distance_ok(opts, language=None):
    """
    Return (ok, details) where ok is True iff every distractor is within the
    language-specific cosine-similarity band relative to the correct option.
    """
    if not opts or len(opts) != 4:
        return False, "options list malformed"
    band = SEMANTIC_DISTANCE_BAND.get((language or "").lower(), SEMANTIC_DISTANCE_BAND["default"])
    try:
        sims = _embedding_similarities(opts)
    except Exception as e:
        # If the embedding model fails, do not block generation; log and accept.
        safe_print(f"  [SEMANTIC DISTANCE] embedding model failed: {e}")
        return True, "embedding model unavailable, accepting options"
    bad = []
    for i, sim in enumerate(sims, start=1):
        if sim < band["min"]:
            bad.append(f"option {i} too dissimilar (cos={sim:.2f} < {band['min']})")
        elif sim > band["max"]:
            bad.append(f"option {i} too similar (cos={sim:.2f} > {band['max']})")
    return (not bad, "; ".join(bad) if bad else "all distractors in band")


def _sanitize_semantic_distance(opts, language, all_meanings, df_all, rng, max_attempts=8):
    """
    Replace distractors that fall outside the semantic band with fallback
    distractors that are inside the band. Returns (sanitized_opts, n_replaced).
    This avoids benching a generator just because one option is a near-paraphrase
    or an unrelated outlier.
    """
    if not opts or len(opts) != 4:
        return opts, 0
    band = SEMANTIC_DISTANCE_BAND.get((language or "").lower(), SEMANTIC_DISTANCE_BAND["default"])
    sanitized = list(opts)
    replaced = 0
    try:
        sims = _embedding_similarities(sanitized)
    except Exception as e:
        safe_print(f"  [SEMANTIC SANITIZE] embedding model failed: {e}")
        return sanitized, 0

    existing = {str(o).strip().lower() for o in sanitized}
    for idx in range(1, 4):
        attempt = 0
        while attempt < max_attempts:
            sim = sims[idx - 1]
            if band["min"] <= sim <= band["max"]:
                break
            # Sample a fallback distractor and test it.
            alt = semantically_distinct_negative_sample(
                sanitized[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=existing
            )[0]
            alt_stripped = str(alt).strip()
            if alt_stripped.lower() in existing:
                attempt += 1
                continue
            test_opts = [sanitized[0]] + [alt_stripped if i == idx else sanitized[i] for i in range(1, 4)]
            try:
                test_sims = _embedding_similarities(test_opts)
            except Exception:
                attempt += 1
                continue
            alt_sim = test_sims[idx - 1]
            if band["min"] <= alt_sim <= band["max"]:
                sanitized[idx] = alt_stripped
                existing.add(alt_stripped.lower())
                sims[idx - 1] = alt_sim
                replaced += 1
                break
            attempt += 1
    return sanitized, replaced


# ── NLI paraphrase filter ───────────────────────────────────────────────────

def _nli_entailment_score(premise, hypothesis):
    """
    Return the NLI entailment probability for premise -> hypothesis.
    Returns 0.0 if the NLI model is unavailable.
    """
    model = _load_nli_model()
    if not model:
        return 0.0
    try:
        scores = model.predict([[str(premise), str(hypothesis)]], apply_softmax=True)[0]
        # Labels are typically [contradiction, entailment, neutral]
        return float(scores[1])
    except Exception as e:
        safe_print(f"  [NLI] prediction failed: {e}")
        return 0.0


def nli_paraphrase_filter_ok(opts, threshold=None, language=None):
    """
    Return (ok, details) where ok is True iff no distractor entails or is
    entailed by the correct meaning (index 0). Paraphrase is symmetric, so we
    check both directions.
    """
    if not opts or len(opts) != 4:
        return False, "options list malformed"
    if threshold is None:
        threshold = NLI_ENTAILMENT_THRESHOLD
    guard = _nli_embedding_guard(language)
    correct = str(opts[0]).strip()
    bad = []
    for i, distractor in enumerate(opts[1:], start=1):
        d = str(distractor).strip()
        forward = _nli_entailment_score(d, correct)
        backward = _nli_entailment_score(correct, d)
        flagged = forward >= threshold or backward >= threshold
        if flagged:
            try:
                emb_sim = float(_embedding_similarities([correct, d])[0])
            except Exception:
                emb_sim = 0.0
            if emb_sim <= guard:
                flagged = False
        if flagged:
            bad.append(f"option {i} NLI entailment fwd={forward:.2f} bwd={backward:.2f}")
    return (not bad, "; ".join(bad) if bad else "no NLI entailment detected")


def _sanitize_nli_paraphrases(opts, language, all_meanings, df_all, rng, threshold=None, max_attempts=8):
    """
    Replace distractors that NLI flags as entailing/entailed by the correct meaning.
    Returns (sanitized_opts, n_replaced).
    """
    if not opts or len(opts) != 4:
        return opts, 0
    if threshold is None:
        threshold = NLI_ENTAILMENT_THRESHOLD
    sanitized = list(opts)
    replaced = 0
    if not USE_NLI_FILTER:
        return sanitized, replaced
    existing = {str(o).strip().lower() for o in sanitized}
    for idx in range(1, 4):
        attempt = 0
        while attempt < max_attempts:
            forward = _nli_entailment_score(sanitized[idx], sanitized[0])
            backward = _nli_entailment_score(sanitized[0], sanitized[idx])
            flagged = forward >= threshold or backward >= threshold
            if flagged:
                try:
                    emb_sim = float(_embedding_similarities([sanitized[0], sanitized[idx]])[0])
                except Exception:
                    emb_sim = 0.0
                if emb_sim <= _nli_embedding_guard(language):
                    flagged = False
            if not flagged:
                break
            alt = semantically_distinct_negative_sample(
                sanitized[0], all_meanings, rng, n=1, language=language, df_all=df_all, exclude=existing
            )[0]
            alt_stripped = str(alt).strip()
            if alt_stripped.lower() in existing:
                attempt += 1
                continue
            sanitized[idx] = alt_stripped
            existing.add(alt_stripped.lower())
            replaced += 1
            break
    return sanitized, replaced


# ── Blind shortcut audit ────────────────────────────────────────────────────

def extract_choice(text):
    """Extract a single A-D choice. Normalise output to uppercase A-D or None."""
    if not text:
        return None
    text = text.strip()

    # Strip chain-of-thought / reasoning tags, markdown, bold/italic, fences, JSON wrappers.
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

    # Explicit final-answer patterns (use LAST match — closest to conclusion).
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

    # Look for "A)", "(B)", "C." anywhere in the text.
    marker_match = re.search(r"(?:^|\s|\()([A-Da-d])[\.\):](?=\s|$)", text)
    if marker_match:
        return marker_match.group(1).upper()

    # Last resort: scan for standalone letters, avoiding English words that start with 'a'.
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
        ("{\"0\":\"A\", \"1\":\"B\", \"2\":\"C\", \"3\":\"D\"}", ["A", "B", "C", "D"]),
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
        ("```json\\n{\\\"answer\\\": \\\"C\\\"}\\n```", "C"),
        ("E", None),
        ("", None),
    ]
    for text, expected in letter_cases:
        got = extract_choice(text)
        if got != expected:
            raise AssertionError(f"extract_choice failed on {text!r}: expected {expected}, got {got}")

    safe_print("Parser self-test passed")


def audit_one_mcq(options_dict, correct_label, variant_name, mcq_id, committee_pool, proverb=None):
    """
    Collect A-D votes from the active audit committee.
    By default the audit is blind (options only). If `proverb` is provided,
    the prompt includes the source proverb so the MCQ is answerable from context.
    Records hard/soft failures into the committee pool and brings in substitutes
    when a model's failure threshold is reached.
    """
    text = "\n".join([f"{k}. {v}" for k, v in options_dict.items()])
    if proverb:
        user_content = f"Proverb: {proverb}\n\nWhich option best captures the meaning of this proverb?\n\n{text}"
    else:
        user_content = f"Which option is correct?\n\n{text}"
    messages = [
        {"role": "system", "content": "Reply ONLY with A, B, C, or D."},
        {"role": "user", "content": user_content},
    ]
    prompt_tokens_est = sum(len(m["content"].split()) for m in messages) + 20

    votes = {}
    # Snapshot active committee; substitutions mid-loop apply to the next MCQ.
    for model in list(committee_pool.active):
        # Skip auditors benched earlier in this snapshot.
        if model not in committee_pool.active:
            continue
        cost_tracker.check()
        if cost_tracker.would_exceed(model, prompt_tokens_est, MAX_TOKENS_AUDIT):
            votes[model] = None
            committee_pool.record_failure(model, weight=2, reason="cost_would_exceed")
            RAW_OUTPUTS.append({
                "stage": "audit",
                "variant": variant_name,
                "mcq_id": mcq_id,
                "model": model,
                "prompt": messages[1]["content"],
                "raw_model_output": "",
                "finish_reason": None,
                "extracted_vote": None,
                "error": "cost_would_exceed",
            })
            continue
        try:
            resp = openrouter_chat(model, messages, max_tokens=MAX_TOKENS_AUDIT)
            vote_text = extract_text(resp)
            finish_reason = extract_finish_reason(resp)
            prompt_tok, out_tok = extract_usage(resp)
            cost_tracker.add(model, prompt_tok or prompt_tokens_est, out_tok, "audit")

            if not vote_text or not vote_text.strip():
                raise ValueError("Empty audit response")
            if finish_reason == "length":
                raise ValueError("Truncated audit response (finish_reason=length)")

            vote = extract_choice(vote_text)
            if vote is None:
                # Soft failure: got a response but could not parse A-D vote.
                committee_pool.record_failure(model, weight=1, reason="unparseable_vote")
                votes[model] = None
            else:
                committee_pool.reset_failure_streak(model)
                votes[model] = vote

            RAW_OUTPUTS.append({
                "stage": "audit",
                "variant": variant_name,
                "mcq_id": mcq_id,
                "model": model,
                "prompt": messages[1]["content"],
                "raw_model_output": vote_text,
                "finish_reason": finish_reason,
                "extracted_vote": vote,
            })
        except Exception as e:
            votes[model] = None
            committee_pool.record_failure(model, weight=2, reason=f"audit_exception:{type(e).__name__}")
            RAW_OUTPUTS.append({
                "stage": "audit",
                "variant": variant_name,
                "mcq_id": mcq_id,
                "model": model,
                "prompt": messages[1]["content"],
                "raw_model_output": "",
                "finish_reason": None,
                "extracted_vote": None,
                "error": str(e),
            })
    return votes


def compute_consensus(votes, correct_label, mcq_id=None):
    """
    Plurality consensus among auditors.
    Returns (consensus_label, consensus_frac, consensus_correct).
    If there is a tie for the top label, a deterministic hash of mcq_id is
    used to break the tie without human judgment.
    """
    valid = [v for v in votes.values() if v is not None]
    if not valid:
        return None, 0.0, 0
    counter = Counter(valid)
    ranked = counter.most_common()
    top_count = ranked[0][1]
    top_labels = [label for label, c in ranked if c == top_count]
    if len(top_labels) > 1:
        # Deterministic tie-break: hash mcq_id to pick among tied labels.
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

def load_existing_outputs():
    """Load any CSVs from a previous partial run."""
    mcqs_path = os.path.join(OUTPUT_DIR, "pilot1_test_generated_mcqs.csv")
    audit_path = os.path.join(OUTPUT_DIR, "pilot1_test_audit_results.csv")

    all_mcqs = []
    audit_records = []
    generated_ids = set()
    audited_ids = set()

    if os.path.exists(mcqs_path):
        df = pd.read_csv(mcqs_path, encoding="utf-8-sig")
        all_mcqs = df.to_dict("records")
        generated_ids = {r["mcq_id"] for r in all_mcqs}
        safe_print(f"Resumed {len(all_mcqs)} generated MCQs from {mcqs_path}")

    if os.path.exists(audit_path):
        df = pd.read_csv(audit_path, encoding="utf-8-sig")
        audit_records = df.to_dict("records")
        audited_ids = {r["mcq_id"] for r in audit_records}
        safe_print(f"Resumed {len(audit_records)} audit records from {audit_path}")

    return all_mcqs, audit_records, generated_ids, audited_ids


def save_state(generator_pool, committee_pool, generated_ids, audited_ids,
               generation_done=False, audit_done=False):
    """Persist pool state, cost, completed mcq_id sets, and position counter for resume."""
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost_spent": cost_tracker.spent,
        "cost_history": cost_tracker.history,
        "generator_pool": generator_pool.state_dict(),
        "committee_pool": committee_pool.state_dict(),
        "generated_mcq_ids": sorted(generated_ids),
        "audited_mcq_ids": sorted(audited_ids),
        "generation_done": generation_done,
        "audit_done": audit_done,
        "position_counter": POSITION_COUNTER,
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def flush_csv_outputs(all_mcqs, audit_records):
    """Write intermediate CSVs without overwriting the final summary."""
    mcqs_path = os.path.join(OUTPUT_DIR, "pilot1_test_generated_mcqs.csv")
    audit_path = os.path.join(OUTPUT_DIR, "pilot1_test_audit_results.csv")
    raw_path = os.path.join(OUTPUT_DIR, "pilot1_test_raw_outputs.csv")

    if all_mcqs:
        pd.DataFrame(all_mcqs).to_csv(mcqs_path, index=False, encoding="utf-8-sig")
    if audit_records:
        audit_df = pd.DataFrame(audit_records)
        # Write missing votes/hits as empty strings to avoid pandas float inference.
        for col in audit_df.columns:
            if col.startswith("vote_") or col.startswith("hit_"):
                audit_df[col] = audit_df[col].apply(lambda x: x if pd.notna(x) and x != "" else "")
        audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    if RAW_OUTPUTS:
        pd.DataFrame(RAW_OUTPUTS).to_csv(raw_path, index=False, encoding="utf-8-sig")


def validate_outputs(mcqs_df, audit_df):
    """Post-run sanity check to catch silent parse/API disasters."""
    issues = []
    if mcqs_df.empty:
        issues.append("No MCQs generated")
    else:
        bad_statuses = {"hard_fallback", "parse_fallback"}
        fb_rate = mcqs_df["generation_status"].isin(bad_statuses).mean()
        if fb_rate > 0.25:
            issues.append(f"High generation fallback rate: {fb_rate:.1%}")
        hard_rate = (mcqs_df["generation_status"] == "hard_fallback").mean()
        if hard_rate > 0.25:
            issues.append(f"High hard-fallback (empty/API) rate: {hard_rate:.1%}")
        if "duplicate_options" in mcqs_df.columns:
            dup_rate = mcqs_df["duplicate_options"].mean()
            if dup_rate > 0.05:
                issues.append(f"High duplicate-options rate: {dup_rate:.1%}")
        if "correct_label" in mcqs_df.columns and len(mcqs_df) >= 4:
            pos_dist = mcqs_df["correct_label"].value_counts(normalize=True)
            if pos_dist.max() > 0.35:
                issues.append(f"Position imbalance: {pos_dist.idxmax()} has {pos_dist.max():.1%} correct answers")

    if audit_df.empty:
        issues.append("No audit records")
    else:
        for model in committee_pool.active + committee_pool.benched:
            col = f"vote_{model.replace('/', '_')}"
            if col in audit_df.columns:
                missing = audit_df[col].isna() | (audit_df[col].astype(str) == "")
                none_rate = missing.mean()
                if none_rate > 0.25:
                    issues.append(f"Auditor {model} missing votes: {none_rate:.1%}")

    if issues:
        safe_print("VALIDATION ISSUES:")
        for issue in issues:
            safe_print("  " + issue)
    else:
        safe_print("Output validation passed")
    return issues


# ── Preflight checks ────────────────────────────────────────────────────────

def preflight_check(df_sample, df_all, generator_pool, committee_pool):
    """FBI/CIA-style preflight: verify connectivity, response shapes, and cost envelope."""
    global USE_SELF_CRITIQUE
    safe_print("\n=== PREFLIGHT CHECK ===")
    safe_print(f"API key present: {bool(OPENROUTER_API_KEY)} ({len(OPENROUTER_API_KEY)} chars)")
    safe_print(f"Active generator pool: {generator_pool.active}")
    safe_print(f"Benched generators: {generator_pool.benched}")
    safe_print(f"Active audit committee: {committee_pool.active}")
    safe_print(f"Benched auditors: {committee_pool.benched}")
    safe_print(f"Prompt variants: {[v['name'] for v in PROMPT_VARIANTS]}")
    safe_print(f"Test sample size: {len(df_sample)} proverbs")
    safe_print(f"Cost cap: ${COST_CAP_USD}")
    safe_print(f"Generation max_tokens: {MAX_TOKENS_GEN} (high ceiling; reasoning models use max_completion_tokens)")
    safe_print(f"Self-critique enabled: {USE_SELF_CRITIQUE} (critic: {CRITIC_MODEL})")
    safe_print(f"Audit max_tokens: {MAX_TOKENS_AUDIT}")

    # 1. Parser sanity check (catches regressions before any API spend).
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

    all_pool_models = list(dict.fromkeys(generator_pool.pool + committee_pool.pool))
    refresh_price_table(all_pool_models)

    generator_pool.filter_by_catalog(live_models)
    committee_pool.filter_by_catalog(live_models)

    active_target_models = list(dict.fromkeys(generator_pool.active + committee_pool.active))
    missing = [m for m in active_target_models if live_models and m not in live_models]
    if missing:
        safe_print(f"WARN: these active models are missing from the live catalog: {missing}")
    else:
        safe_print("All active models found in live catalog.")

    # 3. Cheap per-model API probe (~$0.0001 each) to catch routing/empty-content issues.
    safe_print("\n-- Cheap API probes (echo letter A) --")
    for model in list(generator_pool.active):
        if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
            generator_pool.record_failure(model, weight=2, reason="cheap_preflight_failed")
    for model in list(committee_pool.active):
        if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
            committee_pool.record_failure(model, weight=2, reason="cheap_preflight_failed")
    # Probe the critic model if self-critique is enabled.
    if USE_SELF_CRITIQUE and CRITIC_MODEL:
        if not api_preflight(CRITIC_MODEL, max_tokens=MAX_TOKENS_AUDIT):
            safe_print(f"WARN: critic model {CRITIC_MODEL} failed cheap preflight; disabling self-critique.")
            USE_SELF_CRITIQUE = False
    # Also probe likely substitutes so we don't promote a broken model.
    for model in generator_pool.pool + committee_pool.pool:
        if model not in generator_pool.active and model not in generator_pool.benched \
                and model not in committee_pool.active and model not in committee_pool.benched:
            if not api_preflight(model, max_tokens=MAX_TOKENS_AUDIT):
                # Determine which pool owns this model and exclude it.
                if model in generator_pool.pool:
                    generator_pool.exclude(model, reason="cheap_preflight_failed")
                if model in committee_pool.pool:
                    committee_pool.exclude(model, reason="cheap_preflight_failed")

    if len(generator_pool.active) < MIN_ACTIVE_GENERATORS:
        safe_print(f"ABORT: only {len(generator_pool.active)} active generators after cheap probes (need {MIN_ACTIVE_GENERATORS}).")
        return False
    if len(committee_pool.active) < MIN_ACTIVE_COMMITTEE:
        safe_print(f"ABORT: only {len(committee_pool.active)} active auditors after cheap probes (need {MIN_ACTIVE_COMMITTEE}).")
        return False

    # Probe generators using the REAL generation path. Keep probing until every
    # active generator (including newly promoted substitutes) has passed.
    safe_print("\n-- Generator probes (real generation path) --")
    probe_rng = random.Random(SEED + 999)
    probe_row = df_sample.iloc[0]
    probe_variant = PROMPT_VARIANTS[0]
    probe_opts_by_generator = {}
    probed = set()

    while True:
        remaining = [m for m in generator_pool.active if m not in probed]
        if not remaining:
            break
        gen = remaining[0]
        probed.add(gen)
        try:
            cost_tracker.check()
            opts, meta = generate_options(
                probe_row["proverb"], probe_row["meaning"], probe_row["language"],
                probe_variant, probe_rng, df_all["meaning"].dropna().unique().tolist(),
                df_all, gen
            )
            if meta.get("status") in ("parse_fallback", "hard_fallback") or len(opts) != 4:
                safe_print(f"  [FAIL] {gen}: generation status={meta.get('status')} opts={opts}")
                safe_print(f"         error: {meta.get('error', 'unknown')}")
                for entry in reversed(RAW_OUTPUTS):
                    if entry.get("stage") == "generation" and entry.get("generator_model") == gen:
                        safe_print(f"         raw_model_output: {entry.get('raw_model_output', '')[:500]!r}")
                        safe_print(f"         finish_reason: {entry.get('finish_reason')}")
                        break
                generator_pool.record_failure(gen, weight=meta.get("failure_weight", 1), reason=f"preflight:{meta.get('status')}")
            else:
                probe_opts_by_generator[gen] = opts
                generator_pool.reset_failure_streak(gen)
                safe_print(f"  [OK] {gen}: status={meta.get('status')} opts={opts}")
        except Exception as e:
            safe_print(f"  [FAIL] {gen}: {e}")
            generator_pool.record_failure(gen, weight=2, reason=f"preflight_exception:{type(e).__name__}")

    if len(generator_pool.active) < MIN_ACTIVE_GENERATORS:
        safe_print(f"ABORT: only {len(generator_pool.active)} active generators (need {MIN_ACTIVE_GENERATORS}).")
        return False

    # Probe auditors using the REAL audit path on one generated MCQ.
    safe_print("\n-- Audit probes (real audit path) --")
    if not probe_opts_by_generator:
        safe_print("ABORT: no generator produced a usable probe MCQ for audit preflight.")
        return False

    probe_opts = list(probe_opts_by_generator.values())[0]
    probe_options_dict = {"A": probe_opts[0], "B": probe_opts[1], "C": probe_opts[2], "D": probe_opts[3]}
    probed_auditors = set()

    while True:
        remaining = [m for m in committee_pool.active if m not in probed_auditors]
        if not remaining:
            break
        aud = remaining[0]
        probed_auditors.add(aud)
        try:
            cost_tracker.check()
            resp = openrouter_chat(aud, [
                {"role": "system", "content": "Reply ONLY with A, B, C, or D."},
                {"role": "user", "content": f"Which option is correct?\n\n" + "\n".join(f"{k}. {v}" for k, v in probe_options_dict.items())},
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
                committee_pool.record_failure(aud, weight=1, reason="preflight:unparseable_vote")
                safe_print(f"  [FAIL] {aud}: could not extract A-D vote (got {vote})")
            else:
                committee_pool.reset_failure_streak(aud)
                safe_print(f"  [OK] {aud}: vote={vote}")
        except Exception as e:
            safe_print(f"  [FAIL] {aud}: {e}")
            committee_pool.record_failure(aud, weight=2, reason=f"preflight_exception:{type(e).__name__}")

    if len(committee_pool.active) < MIN_ACTIVE_COMMITTEE:
        safe_print(f"ABORT: only {len(committee_pool.active)} active auditors (need {MIN_ACTIVE_COMMITTEE}).")
        return False

    # Cost envelope estimate
    n_mcqs = len(generator_pool.active) * len(PROMPT_VARIANTS) * len(df_sample)
    gen_input_est = 300
    gen_output_est = 200
    audit_input_est = 200
    audit_output_est = 10
    gen_est = sum(cost_tracker.estimate(m, gen_input_est, gen_output_est) for m in generator_pool.active) * len(PROMPT_VARIANTS) * len(df_sample)
    audit_est = sum(cost_tracker.estimate(m, audit_input_est, audit_output_est) for m in committee_pool.active) * n_mcqs
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
        safe_print("WARNING: estimated cost exceeds 50% of cap (acceptable for a test).")

    safe_print("PREFLIGHT PASSED\n")
    return True


# ── Main pipeline ───────────────────────────────────────────────────────────

def main():
    global generator_pool, committee_pool, cost_tracker, POSITION_COUNTER

    safe_print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Pilot 1 TEST with dynamic model pools")
    safe_print(f"Cost cap: ${COST_CAP_USD}")

    # Load & sample
    df_all = load_data()
    df_sample = sample_per_language(df_all, N_PER_LANG, SEED)
    df_sample = df_sample.reset_index(drop=True)
    all_meanings = df_all["meaning"].dropna().unique().tolist()
    rng = random.Random(SEED)

    safe_print(f"\nSampled {len(df_sample)} proverbs:")
    safe_print(df_sample.groupby("language").size())

    # Rehydrate state if available.
    generation_done = False
    audit_done = False
    if os.path.exists(STATE_PATH):
        safe_print(f"\nFound existing state file: {STATE_PATH}")
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
        generator_pool = ModelPool(
            GENERATOR_POOL, GENERATOR_STARTERS, "GENERATOR",
            state=state.get("generator_pool")
        )
        committee_pool = ModelPool(
            COMMITTEE_POOL, COMMITTEE_STARTERS, "COMMITTEE",
            state=state.get("committee_pool")
        )
        cost_tracker = CostTracker(
            COST_CAP_USD,
            spent=state.get("cost_spent", 0.0),
            history=state.get("cost_history", [])
        )
        POSITION_COUNTER = state.get("position_counter", POSITION_COUNTER)
        generation_done = state.get("generation_done", False)
        audit_done = state.get("audit_done", False)
        safe_print(f"Rehydrated cost: ${cost_tracker.spent:.4f}")
        safe_print(f"Active generators: {generator_pool.active}")
        safe_print(f"Active auditors: {committee_pool.active}")

    # Load any partial outputs.
    all_mcqs, audit_records, generated_ids, audited_ids = load_existing_outputs()

    # Preflight before any expensive loop (skip if already passed in a prior run).
    if not generation_done:
        if not preflight_check(df_sample, df_all, generator_pool, committee_pool):
            save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
            raise RuntimeError("Preflight checks failed. Aborting before main spend.")
        save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)

    # Generate MCQs for each prompt variant + proverb, across all active generators.
    if not generation_done:
        safe_print(f"\n=== Starting generation with active generators: {generator_pool.active} ===")
        for variant in PROMPT_VARIANTS:
            safe_print(f"\n=== Generating with prompt variant: {variant['name']} ===")
            for idx, row in df_sample.iterrows():
                # Snapshot active generators so substitutions apply to the next item.
                for gen in list(generator_pool.active):
                    # Skip models that were benched by an earlier failure in this snapshot.
                    if gen not in generator_pool.active:
                        continue
                    mcq_id = f"{gen.replace('/', '_')}_{variant['name']}_{row['language']}_{idx}"
                    if mcq_id in generated_ids:
                        continue

                    try:
                        opts, meta = generate_options(
                            row["proverb"], row["meaning"], row["language"], variant, rng,
                            all_meanings, df_all, gen
                        )
                    except Exception as e:
                        safe_print(f"  Outer generation failed for {gen} {variant['name']} {row['language']}-{idx}: {e}")
                        opts = _make_generation_fallback(row["meaning"], all_meanings, rng, row["language"], df_all)
                        meta = {"status": "hard_fallback", "error": str(e), "fallback_count": 0, "failure_weight": 2}

                    if meta["status"] in ("parse_fallback", "hard_fallback"):
                        generator_pool.record_failure(gen, weight=meta.get("failure_weight", 1), reason=meta["status"])
                    else:
                        generator_pool.reset_failure_streak(gen)

                    options_dict, correct_label = assemble_mcq(opts, mcq_id)
                    curated_meaning = meta.get("curated_meaning", "")
                    original_meaning = meta.get("original_meaning", row["meaning"])
                    all_mcqs.append({
                        "generator_model": gen,
                        "variant": variant["name"],
                        "mcq_id": mcq_id,
                        "language": row["language"],
                        "sample_id": row["sample_id"],
                        "proverb": row["proverb"],
                        "correct_meaning": curated_meaning if curated_meaning else original_meaning,
                        "original_meaning": original_meaning,
                        "curated_meaning": curated_meaning,
                        "correct_label": correct_label,
                        "option_A": options_dict["A"],
                        "option_B": options_dict["B"],
                        "option_C": options_dict["C"],
                        "option_D": options_dict["D"],
                        "generation_status": meta.get("status", "unknown"),
                        "fallback_count": meta.get("fallback_count", 0),
                        "length_replaced": meta.get("length_replaced", 0),
                        "leak_replaced": meta.get("leak_replaced", 0),
                        "nli_replaced": meta.get("nli_replaced", 0),
                        "duplicate_options": has_duplicate_options(options_dict),
                    })
                    generated_ids.add(mcq_id)

                    if len(generator_pool.active) == 0:
                        flush_csv_outputs(all_mcqs, audit_records)
                        save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
                        raise RuntimeError("No active generators remaining. Generation halted.")

                # Periodic flush every 10 proverbs or at end of variant.
                if idx % 10 == 0 or idx == len(df_sample) - 1:
                    flush_csv_outputs(all_mcqs, audit_records)
                    save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
                    safe_print(f"  Variant {variant['name']} progress: {idx + 1}/{len(df_sample)} rows; cost: ${cost_tracker.spent:.4f}")

            flush_csv_outputs(all_mcqs, audit_records)
            save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
            safe_print(f"  Cumulative cost after variant {variant['name']}: ${cost_tracker.spent:.4f}")

        generation_done = True
        save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=True, audit_done=audit_done)

    # Build DataFrame for downstream analysis and audit resume.
    mcqs_df = pd.DataFrame(all_mcqs)

    # Blind shortcut audit
    if not audit_done:
        safe_print(f"\n=== Running blind shortcut audit with active auditors: {committee_pool.active} ===")
        for _, row in mcqs_df.iterrows():
            if row["mcq_id"] in audited_ids:
                continue

            options_dict = {
                "A": row["option_A"],
                "B": row["option_B"],
                "C": row["option_C"],
                "D": row["option_D"],
            }
            votes = audit_one_mcq(options_dict, row["correct_label"], row["variant"], row["mcq_id"], committee_pool)
            consensus_label, consensus_frac, consensus_correct = compute_consensus(
                votes, row["correct_label"], mcq_id=row["mcq_id"]
            )
            record = {
                "generator_model": row["generator_model"],
                "variant": row["variant"],
                "mcq_id": row["mcq_id"],
                "language": row["language"],
                "correct_label": row["correct_label"],
                "consensus_label": consensus_label,
                "consensus_frac": consensus_frac,
                "consensus_correct": consensus_correct,
            }
            for model, vote in votes.items():
                record[f"vote_{model.replace('/', '_')}"] = vote
                record[f"hit_{model.replace('/', '_')}"] = int(vote == row["correct_label"]) if vote else None
            audit_records.append(record)
            audited_ids.add(row["mcq_id"])

            if len(committee_pool.active) == 0:
                flush_csv_outputs(all_mcqs, audit_records)
                save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
                raise RuntimeError("No active auditors remaining. Audit halted.")

            if len(audit_records) % 10 == 0:
                flush_csv_outputs(all_mcqs, audit_records)
                save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=audit_done)
                safe_print(f"  Audited {len(audit_records)}/{len(mcqs_df)} MCQs; cost: ${cost_tracker.spent:.4f}")

        audit_done = True
        flush_csv_outputs(all_mcqs, audit_records)
        save_state(generator_pool, committee_pool, generated_ids, audited_ids,
                   generation_done=generation_done, audit_done=True)

    # Optional with-proverb baseline audit (context-present answerability check).
    with_proverb_records = []
    with_proverb_df = pd.DataFrame()
    if RUN_WITH_PROVERB_BASELINE and not mcqs_df.empty and committee_pool.active:
        safe_print(f"\n=== Running with-proverb baseline audit with active auditors: {committee_pool.active} ===")
        for _, row in mcqs_df.iterrows():
            options_dict = {
                "A": row["option_A"],
                "B": row["option_B"],
                "C": row["option_C"],
                "D": row["option_D"],
            }
            votes = audit_one_mcq(
                options_dict, row["correct_label"], row["variant"], row["mcq_id"],
                committee_pool, proverb=row["proverb"]
            )
            consensus_label, consensus_frac, consensus_correct = compute_consensus(
                votes, row["correct_label"], mcq_id=row["mcq_id"]
            )
            rec = {
                "generator_model": row["generator_model"],
                "variant": row["variant"],
                "mcq_id": row["mcq_id"],
                "language": row["language"],
                "correct_label": row["correct_label"],
                "consensus_label": consensus_label,
                "consensus_frac": consensus_frac,
                "consensus_correct": consensus_correct,
            }
            for model, vote in votes.items():
                rec[f"vote_{model.replace('/', '_')}"] = vote
                rec[f"hit_{model.replace('/', '_')}"] = int(vote == row["correct_label"]) if vote else None
            with_proverb_records.append(rec)
        with_proverb_df = pd.DataFrame(with_proverb_records)
        wp_path = os.path.join(OUTPUT_DIR, "pilot1_test_with_proverb_baseline.csv")
        with_proverb_df.to_csv(wp_path, index=False, encoding="utf-8-sig")
        safe_print(f"  With-proverb baseline accuracy: {with_proverb_df['consensus_correct'].mean():.1%}")

    audit_df = pd.DataFrame(audit_records)

    # Per-variant summary (split by generator)
    comparison_rows = []
    for generator_model in generator_pool.active + generator_pool.benched:
        gen_sub = audit_df[audit_df["generator_model"] == generator_model]
        for variant_name in [v["name"] for v in PROMPT_VARIANTS]:
            sub = gen_sub[gen_sub["variant"] == variant_name]
            for lang in ["English", "Arabic", "Yoruba"]:
                lang_sub = sub[sub["language"] == lang]
                if len(lang_sub) == 0:
                    continue
                comparison_rows.append({
                    "generator_model": generator_model,
                    "variant": variant_name,
                    "language": lang,
                    "n": len(lang_sub),
                    "consensus_accuracy": lang_sub["consensus_correct"].mean(),
                    "mean_consensus_frac": lang_sub["consensus_frac"].mean(),
                    "flag": flag_accuracy(lang_sub["consensus_correct"].mean()),
                })
            comparison_rows.append({
                "generator_model": generator_model,
                "variant": variant_name,
                "language": "ALL",
                "n": len(sub),
                "consensus_accuracy": sub["consensus_correct"].mean(),
                "mean_consensus_frac": sub["consensus_frac"].mean(),
                "flag": flag_accuracy(sub["consensus_correct"].mean()),
            })

    comparison_df = pd.DataFrame(comparison_rows)

    # Per-model summary (by generator)
    per_model_rows = []
    for generator_model in generator_pool.active + generator_pool.benched:
        gen_sub = audit_df[audit_df["generator_model"] == generator_model]
        for model in committee_pool.active + committee_pool.benched:
            col = f"hit_{model.replace('/', '_')}"
            if col not in gen_sub.columns:
                continue
            valid = gen_sub[col].notna() & (gen_sub[col].astype(str) != "")
            if valid.sum() == 0:
                continue
            per_model_rows.append({
                "generator_model": generator_model,
                "model": model,
                "accuracy": gen_sub.loc[valid, col].mean(),
                "n": valid.sum(),
            })
    per_model_df = pd.DataFrame(per_model_rows)

    # Print results
    safe_print("\n=== Per-generator/variant consensus accuracy ===")
    for generator_model in generator_pool.active + generator_pool.benched:
        safe_print(f"\nGenerator: {generator_model}")
        sub = comparison_df[comparison_df["generator_model"] == generator_model]
        if not sub.empty:
            safe_print(sub.pivot(index="variant", columns="language", values="consensus_accuracy").round(3).to_string())

    safe_print("\n=== Per-model accuracy by generator ===")
    safe_print(per_model_df.to_string(index=False))

    # Save outputs
    mcqs_path = os.path.join(OUTPUT_DIR, "pilot1_test_generated_mcqs.csv")
    audit_path = os.path.join(OUTPUT_DIR, "pilot1_test_audit_results.csv")
    comparison_path = os.path.join(OUTPUT_DIR, "pilot1_test_prompt_comparison.csv")
    raw_path = os.path.join(OUTPUT_DIR, "pilot1_test_raw_outputs.csv")
    summary_path = os.path.join(OUTPUT_DIR, "pilot1_test_summary.json")

    mcqs_df.to_csv(mcqs_path, index=False, encoding="utf-8-sig")
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")
    if RAW_OUTPUTS:
        pd.DataFrame(RAW_OUTPUTS).to_csv(raw_path, index=False, encoding="utf-8-sig")

    validation_issues = validate_outputs(mcqs_df, audit_df)

    # Compute conventional distractor-quality metrics.
    distractor_metrics = compute_distractor_metrics(mcqs_df)
    distractor_metrics_path = os.path.join(OUTPUT_DIR, "pilot1_test_distractor_metrics.csv")
    if distractor_metrics:
        pd.DataFrame([distractor_metrics]).to_csv(distractor_metrics_path, index=False, encoding="utf-8-sig")

    # Export a human spot-check sample if enough MCQs were generated.
    export_human_annotation_sample(mcqs_df, audit_df, n=50)

    # Generate publication-ready visualisations.
    committee_models = committee_pool.active + committee_pool.benched
    figure_paths = generate_visualizations(audit_df, mcqs_df, committee_models, OUTPUT_DIR)

    position_dist = mcqs_df["correct_label"].value_counts().to_dict() if not mcqs_df.empty else {}
    duplicate_count = int(mcqs_df["duplicate_options"].sum()) if "duplicate_options" in mcqs_df.columns else 0
    with_proverb_accuracy = (
        float(with_proverb_df["consensus_correct"].mean())
        if not with_proverb_df.empty and "consensus_correct" in with_proverb_df.columns
        else None
    )

    summary = {
        "version": "v70",
        "use_llm_fallback": USE_LLM_FALLBACK,
        "fallback_generator_model": FALLBACK_GENERATOR_MODEL if USE_LLM_FALLBACK else None,
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "n_per_language": N_PER_LANG,
        "generator_pool": generator_pool.state_dict(),
        "committee_pool": committee_pool.state_dict(),
        "substitutions": {
            "generators": generator_pool.substitutions,
            "auditors": committee_pool.substitutions,
        },
        "prompt_variants": [
            {"name": v["name"], "rationale": v["rationale"]} for v in PROMPT_VARIANTS
        ],
        "cost_cap_usd": COST_CAP_USD,
        "estimated_cost_usd": round(cost_tracker.spent, 6),
        "per_variant_comparison": comparison_df.to_dict(orient="records"),
        "per_model_accuracy": per_model_df.to_dict(orient="records"),
        "cost_history": cost_tracker.history,
        "validation_issues": validation_issues,
        "position_distribution": position_dist,
        "duplicate_options_count": duplicate_count,
        "distractor_metrics": distractor_metrics,
        "with_proverb_baseline_accuracy": with_proverb_accuracy,
        "figure_paths": figure_paths,
        "llm_fallback_used": _LLM_FALLBACK_USED,
        "llm_fallback_rejected": _LLM_FALLBACK_REJECTED,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    safe_print(f"\nSaved outputs to {OUTPUT_DIR}")
    safe_print(f"Total estimated cost: ${cost_tracker.spent:.4f} / ${COST_CAP_USD:.2f}")


def compute_distractor_metrics(mcqs_df):
    """Compute conventional distractor-quality statistics using cached embeddings."""
    if mcqs_df.empty:
        return {}
    try:
        model = _load_embedding_model()
    except Exception as e:
        safe_print(f"[METRICS] embedding model unavailable: {e}")
        return {}
    labels = ["A", "B", "C", "D"]
    key_sims = []
    pairwise_sims = []
    lengths = []
    for _, row in mcqs_df.iterrows():
        opts = [row["option_A"], row["option_B"], row["option_C"], row["option_D"]]
        correct = str(row["correct_meaning"]).strip()
        correct_label = row["correct_label"]
        all_texts = [correct] + [str(o).strip() for o in opts]
        try:
            embeddings = model.encode(all_texts, convert_to_numpy=True, show_progress_bar=False)
        except Exception:
            continue
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        embeddings = embeddings / norms
        correct_emb = embeddings[0]
        opt_embs = embeddings[1:]
        for label, opt_emb in zip(labels, opt_embs):
            if label != correct_label:
                key_sims.append(float(opt_emb.dot(correct_emb)))
        for i in range(4):
            for j in range(i + 1, 4):
                pairwise_sims.append(float(opt_embs[i].dot(opt_embs[j])))
        lengths.extend([len(str(o)) for o in opts])
    if not key_sims:
        return {}
    return {
        "n_mcqs": len(mcqs_df),
        "avg_distractor_key_similarity": round(float(np.mean(key_sims)), 4),
        "std_distractor_key_similarity": round(float(np.std(key_sims)), 4),
        "avg_pairwise_option_similarity": round(float(np.mean(pairwise_sims)), 4),
        "std_pairwise_option_similarity": round(float(np.std(pairwise_sims)), 4),
        "option_length_mean": round(float(np.mean(lengths)), 1),
        "option_length_cv": round(float(np.std(lengths) / np.mean(lengths)), 4) if np.mean(lengths) else 0.0,
        "nli_replaced_total": int(mcqs_df["nli_replaced"].sum()) if "nli_replaced" in mcqs_df.columns else 0,
        "duplicate_options_count": int(mcqs_df["duplicate_options"].sum()) if "duplicate_options" in mcqs_df.columns else 0,
    }


def export_human_annotation_sample(mcqs_df, audit_df, n=50):
    """Write a CSV sample for human annotators to spot-check."""
    if mcqs_df.empty or audit_df.empty:
        return
    merged = mcqs_df.merge(
        audit_df[["mcq_id", "consensus_label", "consensus_frac", "consensus_correct"]],
        on="mcq_id",
        how="left",
    )
    # Stratify by language and consensus flag to get a representative sample.
    merged["flag"] = merged["consensus_correct"].apply(flag_accuracy)
    sample_rows = []
    for lang in ["English", "Arabic", "Yoruba"]:
        lang_df = merged[merged["language"] == lang]
        if lang_df.empty:
            continue
        per_flag = n // 9  # 3 languages × 3 flags (PASS/REVIEW/FAIL) roughly
        for flag in ["PASS", "REVIEW", "FAIL"]:
            sub = lang_df[lang_df["flag"] == flag]
            if not sub.empty:
                sample_rows.append(sub.sample(n=min(per_flag, len(sub)), random_state=SEED))
    if sample_rows:
        sample = pd.concat(sample_rows).drop_duplicates(subset=["mcq_id"]).head(n)
    else:
        sample = merged.sample(n=min(n, len(merged)), random_state=SEED)

    out = []
    for _, row in sample.iterrows():
        out.append({
            "item_id": row["mcq_id"],
            "language": row["language"],
            "generator_model": row["generator_model"],
            "variant": row["variant"],
            "proverb": row["proverb"],
            "option_A": row["option_A"],
            "option_B": row["option_B"],
            "option_C": row["option_C"],
            "option_D": row["option_D"],
            "human_answer": "",
            "human_confidence": "",
            "human_notes": "",
            "generation_status": row.get("generation_status", ""),
            "fallback_count": row.get("fallback_count", 0),
            "nli_replaced": row.get("nli_replaced", 0),
            # Answer key columns (annotators should not look before answering)
            "correct_label": row["correct_label"],
            "correct_meaning": row["correct_meaning"],
            "consensus_label": row["consensus_label"],
            "consensus_correct": row["consensus_correct"],
            "flag": row["flag"],
        })
    human_path = os.path.join(OUTPUT_DIR, "pilot1_test_human_annotation_sample.csv")
    pd.DataFrame(out).to_csv(human_path, index=False, encoding="utf-8-sig")
    safe_print(f"Exported {len(out)} items for human annotation to {human_path}")


# ── Visualisation helpers ───────────────────────────────────────────────────

def _short_name(model_id):
    return model_id.split("/")[-1]


def _flag_color(acc):
    if pd.isna(acc):
        return "#95a5a6"
    if acc < 0.30:
        return "#2ecc71"
    elif acc <= 0.45:
        return "#f1c40f"
    return "#e74c3c"


def _save_figure(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_consensus_by_variant(audit_df, output_dir):
    if audit_df.empty:
        return None
    data = audit_df.groupby("variant")["consensus_correct"].mean().reset_index()
    data = data.sort_values("consensus_correct")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(
        data["variant"],
        data["consensus_correct"],
        color=[_flag_color(x) for x in data["consensus_correct"]],
    )
    ax.axvline(0.30, color="green", linestyle="--", linewidth=1.5, label="PASS <30%")
    ax.axvline(0.45, color="orange", linestyle="--", linewidth=1.5, label="REVIEW 30–45%")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Blind Consensus Accuracy")
    ax.set_title("Shortcut Signal by Prompt Variant")
    ax.legend(loc="lower right")
    for bar, val in zip(bars, data["consensus_correct"]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.1%}", va="center")
    path = os.path.join(output_dir, "fig1_consensus_by_variant.png")
    _save_figure(fig, path)
    return path


def plot_consensus_by_language(audit_df, output_dir):
    if audit_df.empty:
        return None
    data = audit_df.groupby("language")["consensus_correct"].mean().reindex(["English", "Arabic", "Yoruba"]).dropna().reset_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        data["language"],
        data["consensus_correct"],
        color=[_flag_color(x) for x in data["consensus_correct"]],
    )
    ax.axhline(0.30, color="green", linestyle="--", linewidth=1.5, label="PASS <30%")
    ax.axhline(0.45, color="orange", linestyle="--", linewidth=1.5, label="REVIEW 30–45%")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Blind Consensus Accuracy")
    ax.set_title("Shortcut Signal by Language")
    ax.legend()
    for bar, val in zip(bars, data["consensus_correct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.1%}", ha="center")
    path = os.path.join(output_dir, "fig2_consensus_by_language.png")
    _save_figure(fig, path)
    return path


def plot_consensus_by_generator(audit_df, output_dir):
    if audit_df.empty:
        return None
    data = audit_df.groupby("generator_model")["consensus_correct"].mean().reset_index()
    data["short_name"] = data["generator_model"].apply(_short_name)
    data = data.sort_values("consensus_correct")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(
        data["short_name"],
        data["consensus_correct"],
        color=[_flag_color(x) for x in data["consensus_correct"]],
    )
    ax.axvline(0.30, color="green", linestyle="--", linewidth=1.5, label="PASS <30%")
    ax.axvline(0.45, color="orange", linestyle="--", linewidth=1.5, label="REVIEW 30–45%")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Blind Consensus Accuracy")
    ax.set_title("Shortcut Signal by Generator")
    ax.legend(loc="lower right")
    for bar, val in zip(bars, data["consensus_correct"]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.1%}", va="center")
    path = os.path.join(output_dir, "fig3_consensus_by_generator.png")
    _save_figure(fig, path)
    return path


def plot_generator_variant_heatmap(audit_df, output_dir):
    if audit_df.empty:
        return None
    pivot = audit_df.pivot_table(
        index="generator_model",
        columns="variant",
        values="consensus_correct",
        aggfunc="mean",
    )
    pivot.index = [_short_name(i) for i in pivot.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pivot.values, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.iloc[i, j]
            text = f"{val:.2f}" if not pd.isna(val) else ""
            ax.text(j, i, text, ha="center", va="center", color="black" if val < 0.5 else "white")
    fig.colorbar(im, ax=ax, label="Consensus Accuracy")
    ax.set_title("Generator × Variant Shortcut Heatmap")
    ax.set_xlabel("Prompt Variant")
    ax.set_ylabel("Generator")
    path = os.path.join(output_dir, "fig4_generator_variant_heatmap.png")
    _save_figure(fig, path)
    return path


def plot_position_distribution(mcqs_df, output_dir):
    if mcqs_df.empty or "correct_label" not in mcqs_df.columns:
        return None
    counts = mcqs_df["correct_label"].value_counts().reindex(["A", "B", "C", "D"]).fillna(0)
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(counts.index, counts.values, color="#3498db")
    ax.axhline(len(mcqs_df) / 4, color="red", linestyle="--", label="Perfect balance")
    ax.set_ylabel("Count")
    ax.set_title("Correct-Answer Position Distribution")
    ax.legend()
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{val}\n({val/len(mcqs_df):.1%})", ha="center")
    path = os.path.join(output_dir, "fig5_position_distribution.png")
    _save_figure(fig, path)
    return path


def plot_generation_status(mcqs_df, output_dir):
    if mcqs_df.empty or "generation_status" not in mcqs_df.columns:
        return None
    status_order = ["generated", "partial", "length_fallback", "parse_fallback", "hard_fallback"]
    counts = mcqs_df["generation_status"].value_counts().reindex(status_order).fillna(0)
    colors = {"generated": "#2ecc71", "partial": "#f1c40f", "length_fallback": "#e67e22", "parse_fallback": "#e74c3c", "hard_fallback": "#c0392b"}
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values, color=[colors.get(k, "#95a5a6") for k in counts.index])
    ax.set_ylabel("Number of MCQs")
    ax.set_title("Generation Status Distribution")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{int(val)}", ha="center")
    path = os.path.join(output_dir, "fig6_generation_status.png")
    _save_figure(fig, path)
    return path


def plot_fallback_rate_by_generator(mcqs_df, output_dir):
    if mcqs_df.empty or "fallback_count" not in mcqs_df.columns:
        return None
    data = mcqs_df.groupby("generator_model").agg(
        n=("mcq_id", "count"),
        fallback_rate=("fallback_count", lambda x: (x > 0).mean()),
    ).reset_index()
    data["short_name"] = data["generator_model"].apply(_short_name)
    data = data.sort_values("fallback_rate")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(data["short_name"], data["fallback_rate"], color="#e67e22")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fraction of MCQs with ≥1 Fallback Distractor")
    ax.set_title("Fallback Rate by Generator")
    for bar, val, n in zip(bars, data["fallback_rate"], data["n"]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.1%} (n={n})", va="center")
    path = os.path.join(output_dir, "fig7_fallback_rate_by_generator.png")
    _save_figure(fig, path)
    return path


def plot_auditor_hit_rates(audit_df, models, output_dir):
    if audit_df.empty or not models:
        return None
    rows = []
    for model in models:
        col = f"hit_{model.replace('/', '_')}"
        if col not in audit_df.columns:
            continue
        valid = audit_df[col].notna() & (audit_df[col].astype(str) != "")
        if valid.sum() == 0:
            continue
        rows.append({"model": _short_name(model), "accuracy": audit_df.loc[valid, col].mean(), "n": valid.sum()})
    if not rows:
        return None
    data = pd.DataFrame(rows).sort_values("accuracy")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(data["model"], data["accuracy"], color="#9b59b6")
    ax.axvline(0.25, color="black", linestyle="--", label="Random baseline")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Individual Auditor Accuracy")
    ax.set_title("Per-Auditor Hit Rate on Blind Options")
    ax.legend()
    for bar, val, n in zip(bars, data["accuracy"], data["n"]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.1%} (n={n})", va="center")
    path = os.path.join(output_dir, "fig8_auditor_hit_rates.png")
    _save_figure(fig, path)
    return path


def plot_cost_breakdown(cost_history, output_dir):
    if not cost_history:
        return None
    df = pd.DataFrame(cost_history)
    if df.empty or "model" not in df.columns or "cost" not in df.columns:
        return None
    data = df.groupby("model")["cost"].sum().reset_index().sort_values("cost", ascending=False).head(12)
    data["short_name"] = data["model"].apply(_short_name)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(data["short_name"], data["cost"], color="#34495e")
    ax.set_xlabel("Estimated Cost (USD)")
    ax.set_title("Cost Breakdown by Model")
    for bar, val in zip(bars, data["cost"]):
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2, f"${val:.3f}", va="center")
    path = os.path.join(output_dir, "fig9_cost_breakdown.png")
    _save_figure(fig, path)
    return path


def plot_consensus_fraction_distribution(audit_df, output_dir):
    if audit_df.empty:
        return None
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(audit_df["consensus_frac"], bins=10, range=(0, 1), color="#1abc9c", edgecolor="black")
    ax.set_xlabel("Consensus Fraction")
    ax.set_ylabel("Number of MCQs")
    ax.set_title("Distribution of Auditor Agreement Strength")
    path = os.path.join(output_dir, "fig10_consensus_fraction_distribution.png")
    _save_figure(fig, path)
    return path


def generate_visualizations(audit_df, mcqs_df, committee_models, output_dir):
    """Create publication-ready figures and return a list of file paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    paths.append(("Shortcut by Variant", plot_consensus_by_variant(audit_df, output_dir)))
    paths.append(("Shortcut by Language", plot_consensus_by_language(audit_df, output_dir)))
    paths.append(("Shortcut by Generator", plot_consensus_by_generator(audit_df, output_dir)))
    paths.append(("Generator × Variant Heatmap", plot_generator_variant_heatmap(audit_df, output_dir)))
    paths.append(("Position Distribution", plot_position_distribution(mcqs_df, output_dir)))
    paths.append(("Generation Status", plot_generation_status(mcqs_df, output_dir)))
    paths.append(("Fallback Rate by Generator", plot_fallback_rate_by_generator(mcqs_df, output_dir)))
    paths.append(("Auditor Hit Rates", plot_auditor_hit_rates(audit_df, committee_models, output_dir)))
    paths.append(("Cost Breakdown", plot_cost_breakdown(cost_tracker.history, output_dir)))
    paths.append(("Consensus Fraction Distribution", plot_consensus_fraction_distribution(audit_df, output_dir)))
    generated = {title: path for title, path in paths if path}
    safe_print(f"Generated {len(generated)} visualisations:")
    for title, path in generated.items():
        safe_print(f"  - {title}: {path}")
    return generated


def flag_accuracy(acc):
    if pd.isna(acc):
        return "N/A"
    if acc < 0.30:
        return "PASS"
    elif acc <= 0.45:
        return "REVIEW"
    else:
        return "FAIL"


if __name__ == "__main__":
    main()
