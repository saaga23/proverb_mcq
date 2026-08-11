#### 3. Methodology: The Hardened Pipeline

### 3.1 Overview

Figure 1 shows the pipeline. Input is a proverb + curated gold meaning. Output is a 4-option MCQ with options Aâ€“D. The pipeline has five stages:

1. **Dynamic generator pool** â€” 3 active models round-robin across 4 prompt variants.
2. **Dual-gate validation** â€” semantic distance band, NLI paraphrase filter, leak sanitizer, length parity, idiom blocklist, duplicate repair.
3. **Corpus fallback sampler** â€” invoked when gates reject all generated distractors.
4. **Option assembly** â€” round-robin correct-key placement (position shuffling inactive in v68; planned for v70).
5. **Blind audit committee** â€” 4 heterogeneous models vote options-only; consensus label computed.

### 3.2 Generator Pool

Active generators (v68):
- `qwen/qwen3.7-max` (Qwen family)
- `google/gemma-4-31b-it` (Google family)
- `google/gemini-2.5-flash` (Google family)

Substitutes: `google/gemini-2.5-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `anthropic/claude-sonnet-4`. Hard-failure threshold: 2 consecutive misses; soft-failure threshold: 5 misses. Zero substitutions occurred in v68.

### 3.3 Prompt Variants

| Variant | Rationale |
|---------|-----------|
| `adversarial-hard-negative` | Forces semantically close distractors rather than obvious reversals |
| `adversarial-length-locked` | Strict length and register parity plus ban on negation/antonym shortcuts |
| `taxonomy-guided` | Haladyna / VERGE taxonomy with tightened surface constraints |
| `overgenerate-select` | Generate 8+ candidates, select 3 most plausible and distinct |

All variants include: Â±45% length parity, no generic English idioms, no lexical overlap with source proverb, no meta-text.

### 3.4 Dual-Gate Validation

**Gate 1 â€” Semantic:**
- NLI paraphrase filter: rejects distractors with NLI entailment > 0.60 and embedding similarity > 0.55 (language-specific: Arabic/Yoruba 0.45, English 0.58).
- Correct-meaning leak sanitizer: replaces distractors echoing the gold meaning (language-specific thresholds: English 0.90, Arabic/Yoruba 0.80).
- Idiom blocklist: rejects generic English idioms as distractors for any language.

**Gate 2 â€” Structural:**
- Length parity: all options within Â±35% of median length; relaxed to Â±45% if all four within band.
- Duplicate repair: near-duplicate options (Jaccard > 0.50) replaced with fallback.
- Offensive guard: rejects vulgar or culturally inappropriate fallback text.

### 3.5 Corpus Fallback Sampler

When Gate 1 or Gate 2 rejects all generated distractors, the pipeline samples from a corpus of other proverbs' meanings. The sampler uses weighted random selection with exclude sets to avoid repeated collisions. In v68, the fallback sampler is the confirmed bottleneck (Section 6).

### 3.6 Blind Audit Committee

Active auditors (v68):
- `meta-llama/llama-3.3-70b-instruct` (Meta)
- `mistralai/mistral-small-3.2-24b-instruct` (Mistral)
- `google/gemma-3-27b-it` (Google)
- `deepseek/deepseek-v3.2` (DeepSeek)

Each auditor receives only the four options (Aâ€“D), no proverb text, no correct meaning. Votes are extracted via regex (uppercase Aâ€“D). Consensus label = plurality vote. Consensus fraction = fraction of auditors agreeing on consensus label. Consensus correct = 1 if consensus label matches correct label.

Position distribution is balanced by round-robin counter (45/45/45/45). Position shuffling is **inactive** in v68; planned for v70.

### 3.7 Cost Cap and Reproducibility

Hard cost cap: $5.00 per run. v68 cost: $0.85. Every API call is logged with model ID, prompt tokens, completion tokens, and cost. Model IDs are versioned in `pilot1_test_summary.json`. OpenRouter catalog snapshot saved at `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`.

---


