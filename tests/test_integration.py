#!/usr/bin/env python3
"""Lightweight integration test: mock OpenRouter responses and run generate_options."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "generation"))
os.environ["OPENROUTER_API_KEY"] = "dummy"

import openrouter_pilot_distractor_generation_test_nano_opus as src

rng = random.Random(20260620)

proverb = "That which does not kill us makes us stronger"
meaning = "Adversity builds resilience."
language = "English"
variant = src.PROMPT_VARIANTS[0]  # adversarial-length-locked
all_meanings = [
    "Family needs should be prioritized.",
    "Public generosity outweighs private needs.",
    "Sacrifice personal comfort for the community.",
    "Prioritize spiritual duties over family.",
    "Comfort builds resilience.",
    "Traumatic injuries heal physical tissue.",
]

# Build a fake OpenRouter response object.
def fake_response(text, finish="stop", prompt_tokens=100, completion_tokens=50):
    return {
        "choices": [{"message": {"content": text}, "finish_reason": finish}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
    }

# Case 1: clean generated options
clean = '["Adversity builds resilience.", "Comfort builds resilience.", "Traumatic injuries heal physical tissue.", "Dangerous situations trigger primal instincts."]'
src.openrouter_chat = lambda *args, **kwargs: fake_response(clean)
opts, meta = src.generate_options(proverb, meaning, language, variant, rng, all_meanings, None, "mock")
print("CASE 1 clean:", meta["status"], "fallbacks", meta["fallback_count"], "nli", meta["nli_replaced"])
print(" opts:", opts)

# Case 2: options contain a generic idiom leak -> should retry then fallback
leak = '["Adversity builds resilience.", "Go big or go home.", "Comfort builds resilience.", "Traumatic injuries heal physical tissue."]'
src.openrouter_chat = lambda *args, **kwargs: fake_response(leak)
opts, meta = src.generate_options(proverb, meaning, language, variant, rng, all_meanings, None, "mock")
print("CASE 2 idiom leak:", meta["status"], meta)
print(" opts:", opts)

# Case 3: duplicate options -> should repair
dup = '["Adversity builds resilience.", "Comfort builds resilience.", "Comfort builds resilience.", "Traumatic injuries heal physical tissue."]'
src.openrouter_chat = lambda *args, **kwargs: fake_response(dup)
opts, meta = src.generate_options(proverb, meaning, language, variant, rng, all_meanings, None, "mock")
print("CASE 3 duplicate:", meta["status"], meta)
print(" opts:", opts)

# Case 4: near-paraphrase of correct meaning -> NLI/semantic filters should replace
paraphrase = '["Adversity builds resilience.", "Hardships build inner resilience.", "Comfort builds resilience.", "Traumatic injuries heal physical tissue."]'
src.openrouter_chat = lambda *args, **kwargs: fake_response(paraphrase)
opts, meta = src.generate_options(proverb, meaning, language, variant, rng, all_meanings, None, "mock")
print("CASE 4 paraphrase:", meta["status"], meta)
print(" opts:", opts)

print("\nIntegration checks complete.")
