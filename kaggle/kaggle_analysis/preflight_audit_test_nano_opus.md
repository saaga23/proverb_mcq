# Preflight Audit: Pilot 1 TEST — Dynamic Model Pools

**Date:** 2026-06-15 (updated 2026-06-19 for v2.2)  
**Notebook:** `openrouter_pilot_distractor_generation_test_nano_opus.ipynb`  
**Source:** `openrouter_pilot_distractor_generation_test_nano_opus.py`  
**Goal:** Low-cost shakedown of the Pilot 1 distractor-generation / blind-audit pipeline before the next scaled Kaggle spend, with automatic model substitution when a model fails.

---

## 1. What this variant changes (and why)

| Item | v2 (previous) | TEST variant (this notebook) | Rationale |
|------|---------------|------------------------------|-----------|
| Generator roster | `openai/gpt-5` only | **Dynamic pool:** 6 starters + ranked substitutes | gpt-5-nano/mini and even full gpt-5 hit output-token / reasoning-token ceilings and produced malformed JSON. Pooling lets us bench a broken model and promote a substitute without stopping the run. |
| Generator starters | — | `qwen/qwen3.5-397b-a17b`, `google/gemma-4-31b-it`, `meta-llama/llama-4-maverick`, `deepseek/deepseek-v4-pro`, `anthropic/claude-opus-4.8`, `qwen/qwen3.7-max` | Diverse families, cheap-to-mid cost. |
| Generator substitutes | — | `google/gemini-2.5-pro`, `google/gemini-2.5-flash`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano` | Reliable backups; the original substitutes (`qwen/qwen3-14b`, `llama-4-scout`, `gpt-4.1`) had high fallback rates in the N=1 smoke test. |
| Audit committee | 4 models (Claude, GPT-5, Gemini, Nemotron free) | **Dynamic pool:** 4 starters + substitutes, **disjoint from generators** | Nemotron free returned empty/unparseable votes; dropped. Keeping the committee disjoint prevents a model from auditing its own distractors — a major methodological concern for reviewers. |
| Audit starters | — | `meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-small-3.2-24b-instruct`, `google/gemma-3-27b-it`, `anthropic/claude-3.5-haiku` | Disjoint from all generator-pool models. `qwen/qwen3-32b` removed after missing 97.8% of votes; `claude-sonnet-4` already removed in v2.1. |
| Audit substitutes | — | `deepseek/deepseek-v3.2`, `amazon/nova-lite-v1` | Also disjoint from the generator pool. `openai/gpt-4o-mini` removed (weak) and `llama-3.1-405b` removed (404 Not Found). |
| Self-critique | Not present | **DISABLED** in v2.2 (`USE_SELF_CRITIQUE = False`) | The critic always found the correct answer and triggered rewrites, but the rewrites did not reduce perfect consensus or high-consensus-wrong rates. Disabled as a controlled ablation; infrastructure remains in place for a future redesign. |
| Meta-text rejection | Not present | `has_meta_text()` treats markdown headings / instruction leaks as parse failures; Yoruba-specific `has_yoruba_english_idiom()` blocklist added in v2.2 | Prevents strings like `**Crafting Options**` and generic English proverbs in Yoruba options from becoming distractors. |
| Length check | Each distractor vs correct meaning | Each option vs median length of all four options | Reduces false `partial`/`length_fallback` flags while preserving length-parity enforcement. |
| `max_tokens` for generation | 1200 | **4096** | High enough to survive reasoning models whose reasoning tokens consume part of the output budget, while still far below context limits. |
| `max_tokens` for audit | 32 | **256** | Still forces a one-letter answer but avoids the 8-token floor that broke GPT-5 and Nemotron in the first run. |
| OpenAI reasoning token handling | `max_tokens` for all | **`max_completion_tokens` for GPT-5 / o-series** | Reasoning tokens bill against the output budget; `max_tokens` can truncate the visible answer. |
| Sample size | 5 per language (75 MCQs × 1 generator) | 3 per language (up to 270 generation calls across active pool) | Keeps estimated spend well under $2 while exercising every prompt variant in every language. |
| Preflight | None | **Strict**: parser self-test → cheap echo probe → live catalog + price refresh → real-generation-path probe + auto-substitution + cost envelope | Each active generator is asked to generate one real MCQ; each active auditor votes on it. Failures are benched and substitutes are probed. Only aborts if the healthy roster drops below the minimum. |
| Fallback strategies | Retries only | Retries + payload fallbacks on 400/422 | If `max_tokens` / `max_completion_tokens` or `response_format` is rejected, the client retries without it. |
| Resume state | None | `pool_state.json` + periodic CSV flushes | Run can resume after a crash, cost-cap halt, or Kaggle session limit. |
| Output validation | None | `validate_outputs()` flags >25% fallback / missing-vote / duplicate-option rates | Catches silent parse/API disasters before the results are interpreted. |
| Correct-answer position bias | Correct answer always placed at A | `assemble_mcq()` deterministically shuffles the correct answer based on `mcq_id`; blind audit uses the resulting key | Prevents always-A bias and gives reviewers a balanced key distribution. |
| Duplicate distractors | Not checked | `has_duplicate_options()` flags exact or near-duplicate options; duplicates are logged but not dropped (to keep generation deterministic) | Surfaces a common distractor-quality failure mode for post-hoc filtering. |

---

## 2. Dynamic pool rules (football-style substitutions)

The `ModelPool` class manages each roster:

- **Starters** = first `N` models in the ranked pool.
- **Substitutes** = remaining models in the pool.
- **Failure weights:**
  - *Hard failure* (weight = 2): API exception, empty response, `finish_reason="length"`.
  - *Soft failure* (weight = 1): response returned but could not be parsed into the required format.
- **Bench threshold:** `fail_threshold = 2`. A model is benched when its weighted failure count reaches 2 (i.e., one hard failure, or two soft failures).
- **Substitution:** when a model is benched, the next available substitute is promoted to active. The run continues; the substitute joins on the next item (not the current one, to avoid wasting calls on a transient failure).
- **Minimum healthy roster:** 2 active generators and 2 active auditors. If the pool cannot maintain this, the run aborts.
- **Live catalog filter:** before preflight, any active model not present in the OpenRouter `/models` catalog is benched and replaced.
- **Disjointness:** no model appears in both the generator pool and the audit-committee pool at the start. Substitutes are also chosen to preserve this property.

---

## 3. Live OpenRouter catalog verification

At runtime the notebook fetches `https://openrouter.ai/api/v1/models` and filters the active pools to models that are actually listed. Substitutes are also pulled from the ranked pool, so the catalog check primarily protects against stale starter IDs.

**Starter generator models:**

| Model | Input $/1M | Output $/1M | Role |
|-------|-----------:|------------:|------|
| `qwen/qwen3.5-397b-a17b` | $0.39 | $0.90 | starter generator |
| `google/gemma-4-31b-it` | $0.12 | $0.36 | starter generator |
| `meta-llama/llama-4-maverick` | $0.15 | $0.60 | starter generator |
| `deepseek/deepseek-v4-pro` | $0.435 | $0.87 | starter generator |
| `anthropic/claude-opus-4.8` | $5.00 | $25.00 | starter generator |
| `qwen/qwen3.7-max` | $1.25 | $3.75 | starter generator |

**Starter audit committee (disjoint from generators):**

| Model | Input $/1M | Output $/1M | Role |
|-------|-----------:|------------:|------|
| `meta-llama/llama-3.3-70b-instruct` | $0.10 | $0.32 | starter auditor |
| `mistralai/mistral-small-3.2-24b-instruct` | $0.075 | $0.20 | starter auditor |
| `google/gemma-3-27b-it` | $0.08 | $0.16 | starter auditor |
| `anthropic/claude-3.5-haiku` | $0.80 | $4.00 | starter auditor |

**Substitutes (used when a starter is benched):**
- Generator: `google/gemini-2.5-pro`, `google/gemini-2.5-flash`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`.
- Committee: `deepseek/deepseek-v3.2`, `amazon/nova-lite-v1`.

---

## 4. Known OpenRouter pitfalls and mitigations

### 4.1 Minimum / rejected / default `max_tokens`

**Risk:** Some providers enforce a minimum output-token value or reject `max_tokens` outright. The first Pilot 1 run saw GPT-5 return `400 Bad Request` when `max_tokens=8` was used for audit. Conversely, omitting `max_tokens` can leave small models on a tight provider default, causing JSON truncation and `parse_fallback`.

**Mitigation:**
- Generation: `MAX_TOKENS_GEN = 4096` — high enough to complete a JSON array of 4 meanings even when reasoning tokens consume part of the budget, low enough to stay inside context limits.
- Audit: `MAX_TOKENS_AUDIT = 256` — comfortably above any sane minimum.
- `openrouter_chat()` still falls back through payload variants: original → without token limit → without `response_format` on HTTP 400/422.

### 4.2 Reasoning tokens consuming the output budget

**Risk:** `openai/gpt-5` (full) and other reasoning models count their internal reasoning tokens against `max_tokens`. Even raising the ceiling to 4096 did not fully eliminate truncation/malformed JSON for generation.

**Mitigation:**
- GPT-5 was moved to the **audit committee only**, where a single letter answer is reliable.
- For all OpenAI reasoning families, `_token_limit_kwargs()` sends `max_completion_tokens` instead of `max_tokens`.
- Hard failures (`finish_reason="length"`, empty content) are benched immediately (weight = 2).

### 4.3 Empty `content` with non-zero usage

**Risk:** Gemini and some routed providers can return a 200 OK with `usage.completion_tokens > 0` but `choices[0].message.content` empty (content-filter / reasoning-only output). This produced 75/75 `parse_fallback` rows in the first run.

**Mitigation:**
- `extract_text()` checks `reasoning`, `refusal`, and `content` in that order and returns whichever is non-empty.
- `generate_options()` captures `finish_reason` and the full response snippet when parsing fails.
- JSON mode is requested but not required; fallback strategies retry without it.

### 4.4 Qwen / Gemma / Llama output formatting quirks

**Risk:** Models can wrap JSON in markdown fences or prepend explanatory text even when instructed not to.

**Mitigation:**
- `clean_model_output()` strips `<think>` / `<reasoning>` tags and extracts the first `[]` block or fenced JSON array.
- `parse_options()` validates that the parsed object is a list of exactly 4 strings, and falls back to regex / line parsing.

### 4.5 Cost overruns

**Risk:** Opus 4.8 is expensive ($25/M output). Running it at full scale can blow the $5 cap.

**Mitigation:**
- `CostTracker.would_exceed()` blocks every call that would push the cumulative spend over the cap.
- `preflight_check()` estimates the full run cost before generation and aborts if the estimate exceeds 90% of the cap.
- The test sample is only 3 proverbs per language, keeping the estimated total around $1.00–$1.50.

### 4.6 Wasting a full run on broken response capture

**Risk:** In the first Pilot 1 run, every generation call returned an empty `raw_model_output`, so all 75 MCQs fell back to corpus sampling — the run produced no usable prompt-variant data. A toy probe might not catch this because the model can answer a trivial prompt correctly while failing the real task.

**Mitigation:**
- `preflight_check()` uses the **real generation path**: it calls `generate_options()` on one actual proverb with the first prompt variant for every active generator.
- It checks the returned status is `generated` or `partial` (not `parse_fallback`) and that 4 options were produced.
- Failed generators are benched and substitutes are probed.
- It then runs the **real audit path** on that MCQ and verifies every active auditor returns A-D.
- This guarantees the exact code path works for the final active roster before the main loop starts.

### 4.7 Audit contamination from overlapping model families

**Risk:** If a model both generates distractors and votes on them, the audit is not independent. Reviewers at top venues will treat this as a serious methodological flaw.

**Mitigation:**
- The generator pool and the audit-committee pool are disjoint by design.
- If a committee substitute is ever promoted, it is also chosen from outside the generator pool.
- The raw outputs and pool state are logged so any overlap can be audited post-hoc.

---

## 5. Cost estimate for the test run

Assumptions (starting roster):
- 3 languages × 3 proverbs = 9 proverbs
- 6 generators × 5 variants × 9 proverbs = 270 generation calls
- 270 MCQs × 4 auditors = 1080 audit calls
- Generation: ~300 prompt tokens, ~200 output tokens
- Audit: ~200 prompt tokens, ~10 output tokens

| Component | Estimated cost |
|-----------|---------------:|
| Preflight probes | ~$0.003 |
| Generation (6 starter models) | ~$0.37 |
| Audit (4 starter models × 270 MCQs) | ~$0.60 |
| **Total** | **~$1.00** |

**Headroom vs $5 cap:** ~80%. Substitutes may add a small amount if several starters are benched, but the cap remains hard.

---

## 6. Metrics and shortcut-detection methodology

The notebook uses a **blind options-only audit** to detect surface shortcuts:

1. **No stem leakage:** auditors see only `A. ... B. ... C. ... D. ...`. They do **not** see the proverb or the correct meaning.
2. **Plurality consensus:** `compute_consensus()` collects valid A-D votes from the active auditors. The most common label is the consensus. If two labels tie for first place, consensus is declared `None` and counted as incorrect (no clear consensus).
3. **Shortcut signal:** If consensus accuracy is far above the random baseline (~25%), the distractors contain surface cues that let models pick the correct answer without understanding the proverb.
4. **Flag thresholds:**
   - `< 30%` → `PASS` (distractors are hard / no obvious shortcut)
   - `30–45%` → `REVIEW`
   - `> 45%` → `FAIL` (strong shortcut / distractors too easy)
5. **Per-model accuracy:** Each auditor's hit rate is reported separately, so we can spot a model that is systematically solving by surface cues.

**Why this is the right metric for Pilot 1:**
- The research base (MoMentS, NoisyBench) treats a blind audit as the gold-standard shortcut test.
- Consensus (not single-model accuracy) reduces spurious signals from one flaky auditor.
- The tie-handling rule prevents a 2-2 split from being interpreted as a meaningful consensus.

**Important limitation:** The blind audit detects *surface shortcuts*, not *human validity*. A low consensus score is necessary but not sufficient evidence that the MCQs are good for human test-takers. Human validation is required for that claim.

---

## 7. Local validation

- `python -m py_compile openrouter_pilot_distractor_generation_test_nano_opus.py` passes.
- Notebook JSON loads cleanly and retains 7 cells.
- Module imports successfully; generator and committee pools are disjoint (`overlap == set()`).
- `ModelPool` substitution logic was exercised in isolation:
  - A hard failure (weight=2) immediately benches the model and promotes the next substitute.
  - A soft failure (weight=1) increments the counter; a second soft failure triggers substitution.
- `parser_self_test()` passes; `assemble_mcq()` produces an A-D distribution that is not biased to A across the 9 sample MCQs.
- `has_duplicate_options()` correctly flags exact duplicates and passes non-duplicates.
- The actual OpenRouter pipeline was **not** run locally to avoid API spend.

---

## 8. Pre-flight checklist before running on Kaggle

1. **Upload the new notebook** `openrouter_pilot_distractor_generation_test_nano_opus.ipynb`.
2. **Kaggle Secret:** ensure `OPENROUTER_API_KEY` is set in Kaggle Secrets (no key in code).
3. **Input data:** the notebook hardcodes the dataset path and falls back to `actual_data/cleaned` locally; on Kaggle it will use `/kaggle/input/datasets/abrahamsunday123/full-data-complete`.
4. **No prompt-variant upload needed:** the JSON is embedded as base64 in cell 1.
5. **Expected runtime:** network-bound; 30–60 minutes depending on model speed and substitutions.
6. **Budget:** hard $5 cap is enforced; expected spend ~$1.00–$1.50.
7. **Resume safety:** if the session ends early, re-running the notebook will load `pool_state.json` and skip already-completed MCQ ids.

---

## 9. What to look at after the Kaggle run

1. **`pilot1_test_raw_outputs.csv`** — confirm non-empty `raw_model_output` for generation rows (this was the failure mode in the first run).
2. **`pilot1_test_generated_mcqs.csv`** — check that `generation_status` is mostly `generated`/`partial` rather than `hard_fallback`/`parse_fallback`, that `correct_key` is evenly distributed across A-D, and that `duplicate_options` is rare.
3. **`pilot1_test_audit_results.csv`** — check that all active auditors contribute votes; columns for benched models will be mostly `None`.
4. **`pilot1_test_prompt_comparison.csv`** — compare consensus accuracy across generators and prompt variants.
5. **`pilot1_test_summary.json`** — verify actual cost vs estimate, inspect cost history, `validation_issues`, and final pool states.
6. **`pool_state.json`** — inspect which models were benched and which substitutes were promoted.

If generation still returns empty content, the raw-output logs will contain the full response shape to diagnose whether the issue is OpenRouter routing, content filtering, or provider-specific formatting.

---

## 10. Recommendations

- **Run this TEST notebook first** with `N_PER_LANG = 3`. If the response-capture path is healthy and generation status is mostly `generated`, scale to `N_PER_LANG = 5` or larger.
- If a starter model is benched during preflight, the pool will auto-promote a substitute. Watch the `[POOL] GENERATOR SUBSTITUTION:` lines to see which models are unreliable.
- If the active pool shrinks to the minimum (2 generators or 2 auditors), treat the run as high-risk and fix the failing models before scaling.
- If Opus 4.8 proves too expensive or slow at scale, bench it permanently by moving it lower in `GENERATOR_POOL` (or removing it) so cheaper substitutes take its place.
- **Do not treat the blind-audit consensus as a validity certificate.** Plan a human validation subset (2 native speakers × 50 items) before any submission.
- Do **not** re-use the previous `openrouter_pilot_distractor_generation.ipynb` for the next spend until the response-shape issues are confirmed fixed.

---

## 11. v2 Rebuild — Post-Run Fixes (17 June 2026)

After the first Pilot 1 TEST run produced 47.1% blind consensus (FAIL), the notebook and prompts were rebuilt to address the main failure modes.

### 11.1 What changed

| Fix | Before | After | Rationale |
|-----|--------|-------|-----------|
| **GPT-5 auditor** | `openai/gpt-5` starter — voted on only 2/278 MCQs | Replaced by `anthropic/claude-sonnet-4`; `meta-llama/llama-3.1-405b-instruct` added as substitute | GPT-5 raised ValueError during extraction and was effectively absent. |
| **Vote extraction** | Returned `1.0`/`0.0` floats for some auditors and `1`/`0` for others | Normalised to `A/B/C/D` votes and `1/0` hits; missing votes written as empty strings | Prevents pandas from inferring float columns and makes post-processing consistent. |
| **Prompt variants** | `baseline`, `misconception-based`, `taxonomy-guided`, `few-shot-predictive`, `overgenerate-select` | `adversarial-length-locked`, `adversarial-hard-negative`, `taxonomy-guided`, `few-shot-predictive`, `overgenerate-select` | `baseline` and `misconception-based` produced the worst shortcut signals (61% and 63% consensus). New variants enforce ±20% length parity, register lock, and explicit bans on negation/antonym distractors. |
| **Self-critique loop** | None | Frozen `google/gemini-2.5-flash-preview` critic audits each generated set; if it picks correctly, the generator rewrites distractors once | Directly targets shortcut leakage by making the generator adversarially robust to a blind auditor. |
| **Fallback sampler** | Drew corpus meanings with only Jaccard filtering | Also rejects broken English, multi-sentence fragments, non-sentence starts, duplicates, and meanings too close to the reference | Eliminated garbage like *“in insignificant nail resulted in the loss of the rider...”* and duplicate fallback options. |
| **Correct-key balancing** | MD5-hash position per `mcq_id` produced mild imbalance (B = 20.5%) | Round-robin global counter persisted in state guarantees A-D balance across the run | Removes any residual position bias. |
| **Tie-breaking** | 2-2 ties produced blank consensus labels | Ties broken deterministically by hashing the `mcq_id` and selecting among tied labels | Every MCQ gets a usable consensus label. |
| **Human spot-check export** | None | `export_human_annotation_sample()` writes a stratified 50-item CSV for human review | Bridges the gap between blind audit and human validity. |\n| **Visualisations** | None | 10 PNG figures: consensus by variant/language/generator, generator×variant heatmap, position distribution, generation status, fallback rate, auditor hit rates, cost breakdown, consensus-fraction distribution | Gives reviewers immediate, publication-ready evidence for every claim. |

### 11.2 New guardrails

- **Length parity:** distractors must be within ±20% character count of the correct answer (down from ±35%).
- **No negation/antonym traps:** explicit instruction in every prompt.
- **Critic preflight:** the self-critique model is probed before the main loop; if it fails, self-critique is disabled rather than aborting the run.
- **Position counter in resume state:** `pool_state.json` now stores `position_counter` so resumed runs continue the A-D cycle.

### 11.3 Expected impact

- **Cost:** expected spend rises to ~$1.50–$2.50 because of the critic and rewrite calls, still well under the $5 cap.
- **Quality:** target is to push blind consensus below 30% on the same 9-proverb sample.
- **Risk:** if the new prompts still leak shortcuts, the next lever is to retrieve hard-negative meanings from the corpus or add a human-in-the-loop distractor pass.
