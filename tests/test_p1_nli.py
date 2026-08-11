#!/usr/bin/env python3
"""Local validation of P1 NLI paraphrase filter."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "generation"))

os.environ["OPENROUTER_API_KEY"] = "dummy"

import openrouter_pilot_distractor_generation_test_nano_opus as src

print("Loading NLI model...")
model = src._load_nli_model()
print("Model:", type(model))

# Test direct NLI scores
pairs = [
    ("Charity begins at home.", "One should prioritize their family's needs before helping others."),
    ("Charity begins at home.", "Public duty outweighs private need."),
    ("The neckless gourd will itself indicate to the farmer how to tie it up.", "A person with unusual traits will naturally show the community the specific way they must be managed."),
    ("Adversity builds resilience.", "Hardship develops fortitude."),
    ("Adversity builds resilience.", "Comfort builds resilience."),
]
for correct, distractor in pairs:
    fwd = src._nli_entailment_score(distractor, correct)
    bwd = src._nli_entailment_score(correct, distractor)
    print(f"\nCorrect: {correct}\nDistractor: {distractor}\n  fwd={fwd:.3f} bwd={bwd:.3f}")

# Test filter on full option sets
print("\n=== nli_paraphrase_filter_ok ===")
sets = [
    # Loose paraphrase: NLI does not flag it and embedding distance is moderate,
    # so the filter allows it (semantic band / correct-meaning leak handle stricter echoes).
    (["Charity begins at home.", "One should prioritize their family's needs before helping others.", "Public duty outweighs private need.", "Religious institutions deserve support first."], True),
    # Strong paraphrase with high NLI entailment in both directions.
    (["Adversity builds resilience.", "Hardship develops fortitude.", "Comfort builds resilience.", "Traumatic injuries heal physical tissue."], False),
]
for opts, expected_ok in sets:
    ok, details = src.nli_paraphrase_filter_ok(opts, threshold=0.60)
    status = "OK" if ok == expected_ok else "FAIL"
    print(f"{status}: ok={ok} (expected {expected_ok}) | {details}")

print("\nP1 NLI checks complete.")
