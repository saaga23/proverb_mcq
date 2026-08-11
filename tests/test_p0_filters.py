#!/usr/bin/env python3
"""Quick local validation of P0 post-processing filters."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "generation"))
os.environ["OPENROUTER_API_KEY"] = "dummy"

import openrouter_pilot_distractor_generation_test_nano_opus as src

rng = random.Random(20260620)

# Test correct-meaning leak filter
print("=== has_correct_meaning_leak ===")
examples = [
    (["Charity begins at home.", "Charity begins with strangers.", "Charity begins only in crises.", "Charity begins when requested."], True),
    (["Charity begins at home.", "One should prioritize family before community.", "Public duty outweighs private need.", "Religious institutions deserve support first."], False),
    (["The neckless gourd will itself indicate to the farmer how to tie it up.", "The neckless gourd will itself indicate to the farmer how to tie it up.", "A ladder rests on the ground.", "A person with unusual traits will be exiled."], True),
]
for opts, expected in examples:
    result = src.has_correct_meaning_leak(opts)
    status = "OK" if result == expected else "FAIL"
    print(f"{status}: {result} (expected {expected}) for {opts}")

# Test blocklist on observed v58 leakages
print("\n=== has_generic_english_idiom ===")
idiom_examples = [
    (["East or west, home is best.", "A", "B", "C"], True),
    (["Go big or go home.", "A", "B", "C"], True),
    (["A lion at home, a lamb abroad.", "A", "B", "C"], True),
    (["Make a rod for your own back.", "A", "B", "C"], True),
    (["Family needs come first.", "A", "B", "C"], False),
]
for opts, expected in idiom_examples:
    result = src.has_generic_english_idiom(opts)
    status = "OK" if result == expected else "FAIL"
    print(f"{status}: {result} (expected {expected}) for {opts[0]}")

# Test duplicate detection / repair
print("\n=== has_duplicate_options / repair_duplicate_options ===")
dup_opts_list = [
    ["Stay positive in adversity.", "Stay positive in adversity.", "Comfort builds resilience.", "Adversity builds resilience."],
    ["Hardship develops fortitude.", "Everyone experiences hardship.", "Everyone experiences hardship.", "Hardship develops complacency."],
    ["A", "B", "C", "D"],
]
all_meanings = [
    "Family needs should be prioritized.",
    "Public generosity outweighs private needs.",
    "A bird in the hand is worth two in the bush.",
    "Sacrifice personal comfort for the community.",
    "Prioritize spiritual duties over family.",
]
for opts in dup_opts_list:
    d = {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]}
    has_dup = src.has_duplicate_options(d)
    print(f"duplicate? {has_dup} -> {opts}")
    if has_dup:
        repaired, n_rep = src.repair_duplicate_options(opts, all_meanings, rng, language="English", df_all=None)
        print(f"  repaired ({n_rep} replaced): {repaired}")
        print(f"  still duplicate? {src.has_duplicate_options(dict(zip(['A','B','C','D'], repaired)))}")

# Mock fallback sampler uniqueness/length test
print("\n=== fallback sampler sanity ===")
ref = "Charity begins at home."
all_meanings = [
    "Family needs should be prioritized.",
    "Public generosity outweighs private needs.",
    "A bird in the hand is worth two in the bush.",
    "Sacrifice personal comfort for the community.",
    "Prioritize spiritual duties over family.",
    "East or west, home is best.",
    "A very long meaning that is definitely far beyond the reference length and should be filtered out by the length ratio check so that we do not get length_fallback downstream",
]
for _ in range(3):
    sample = src.semantically_distinct_negative_sample(ref, all_meanings, rng, n=3, language="English", df_all=None)
    print("sample:", sample)
    ok, reason = src.semantic_distance_ok([ref] + sample, language="English")
    print("  semantic ok:", ok, reason)

print("\nP0 filter checks complete.")
