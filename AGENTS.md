# Agent Handover — ProverbGap MCQ (OpenRouter Pilot 1 TEST)

**Project path:** `C:/Users/USER/Downloads/THe proverbeval container/MCQ`

**Current mission:** Generate shortcut-resistant multiple-choice distractors for the ProverbGap dataset using OpenRouter models, validate with a blind options-only audit, and produce publication-ready outputs.

> **Global Elite Research Execution Framework is active.** This project already implements the framework in `docs/Elite_Research_Execution_Plan.md`. For every decision, use plan-before-code, multi-agent mindset, deep web/GitHub/Context7 research, multiple baselines/ablations/statistical tests, reviewer simulation, and E2E smoke tests before scaling. See `~/.kimi/skills/elite-research-framework/SKILL.md` for the global protocol.
>
> **Global Agentic Power User Framework is active.** All coding, automation, and agent-level work here must use RIPER-5 modes, subagents/swarm for parallel exploration/audits, MCP tools proactively, persistent Memory MCP, hooks/guardrails, and verification loops before declaring done. See `~/.kimi/skills/agentic-power-user/SKILL.md` for the global protocol.

## ⚡ Always-Active Stack (No Reminders Needed)

These skills and commands are loaded by default in every session for this repo.

| Layer | Item | Purpose |
|-------|------|---------|
| **Skill** | `elite-research-framework` | Reviewer-proof research rigor. Wins on methodology conflicts. |
| **Skill** | `agentic-power-user` | Execution rigor. RIPER-5, MCP arsenal, verification loops, subagents. |
| **Skill** | `auto-memory` | Auto-persist findings to Memory MCP after significant work. |
| **Skill** | `proverbgap-orchestrator` | Project master workflow: generation, analysis, paper-first, human validation. |
| **Skill** | `ml-paper-coach` | Paper drafting, rebuttals, LaTeX/Markdown, submission checklists. |
| **Skill** | `kaggle-terminal-workflow` | Kaggle push/pull/submit/sync. |
| **Skill** | `document-io` | PDF, DOCX, Markdown read/write for papers and fellowship packages. |
| **Skill** | `mcp-playbook` | Decision matrix for which MCP tool to use in this stack. |
| **MCP** | `.cursor/mcp.json` | 11 project MCPs: memory, sequential-thinking, context7, filesystem, git, git-conflict, html-to-markdown, devutils, diff, time, npm-search. |
| **MCP** | `~/.cursor/mcp.json` / `~/.kimi/mcp.json` | 15 global MCPs including brave-search, perplexity, playwright, network, qrcode, hueshift, tailwind. |
| **Command** | `.kilo/command/wireshark-tshark.md` | tshark packet inspection for API/debug forensics. |
| **Agent** | `.kilo/agent/active-stack.md` | Canonical active skill stack with loading rules and deprecations. |

**Rules:**
- If MCP tools fail, restart Cursor/Kimi (Settings → MCP → reload). Never silently fail.
- Before any significant change, run the smallest E2E smoke test. Evidence required.
- Auto-persist to Memory MCP after significant work. Do not wait to be asked.
- Never ask permission when a working MCP tool can answer; act autonomously.

**Status as of this handover:** v68 N=5 Kaggle run complete and analyzed (2026-06-22). Frozen v67 config produced 180 MCQs for $0.85 but **failed all shortcut-resistance gates** except duplicates and key balance: perfect consensus 41.7%, HCW 27.8%, partial+fallback 43.9%, hard fallback 16.1%. The corpus-based fallback sampler is confirmed as the bottleneck. A v69 LLM-fallback ablation and a v70 N=15 scaling attempt were both blocked when the OpenRouter API key hit its **monthly budget limit** (`403 Budget limit exceeded`). v70 produced 83 MCQs (36 generated, 19 length-fallback, 18 partial, 10 hard-fallback) before crashing with `RuntimeError: No active generators remaining`. **Decision:** stop all Kaggle/OpenRouter runs until budget is renewed; pivot to paper-first using v68 as the production dataset; begin 60-item human validation; draft paper around methodology + reproducible failure taxonomy. The Fatima Fellowship submission package (`fatima_submission_package_2026-06-22/`) is finalized and archived as `.zip`/`.tar.gz`.

---

## 🔑 Key files

| File | Purpose |
|---|---|
| `openrouter_pilot_distractor_generation_test_nano_opus.py` | Full source (config, pools, prompts, generation, semantic/NLI filters, audit, metrics, visualisations). |
| `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` | Kaggle notebook synced from the `.py` source. **Upload this to Kaggle.** |
| `pilot1_prompt_variants.json` | 4 adversarial prompt variants. Embedded as base64 in the notebook; kept as standalone for local use. |
| `convert_test_nano_opus_to_notebook.py` | Converts `.py` + JSON into a self-contained Kaggle notebook. |
| `test_p0_filters.py` | Local validation of blocklist, correct-meaning leak, duplicate repair, and fallback sampler. |
| `test_p1_nli.py` | Local validation of the NLI paraphrase filter. |
| `test_integration.py` | Lightweight mocked integration test of `generate_options`. |
| `test_pilot1_nano_opus_local.py` | Full mocked end-to-end Pilot 1 TEST run (no API credits). |
| `kaggle_upload_pilot1_test/kernel-metadata.json` | Kaggle kernel push metadata. |
| `kaggle_analysis/preflight_audit_test_nano_opus.md` | Methodology and preflight report. |
| `kaggle_run_logs/v69/compare_v68_v69.py` | Robust paired statistical comparison of v68 vs v69 (McNemar, Wilcoxon, bootstrap, gates, decision rule). |
| `kaggle_run_logs/v69/v69_quick_metrics.py` | Standalone v69 metrics + Wilson CIs + quick plots (no v68 required). |
| `kaggle_run_logs/v69/v69_post_download_checklist.md` | Step-by-step checklist to run immediately after v69 outputs download. |
| `kaggle_run_logs/v69/v69_detailed_analysis_report.md` | Template for the v69 deep-analysis report. |
| `paper_first_analysis_2026-06-22_10-42-02.ipynb` | Self-contained, no-API notebook that reproduces v68 paper tables/figures and the 60-item human-validation sample. |
| `next_steps_2026-06-22_10-42-02.md` | Action plan: human validation recruitment, paper drafting, budget renewal. |
| `ProverbGap_State_of_Work_2026-06-22.docx` | 2-page state-of-work document for Fatima Fellowship quota request, with figures and cost table. |
| `fatima_submission_package_2026-06-22/` | Folder containing the DOCX, figures, README, and an Overleaf-ready LaTeX version. |
| `fatima_submission_package_2026-06-22.zip` | Zip of the above for easy sharing. |
| `generate_state_of_work_docx.py` | Script that regenerates the state-of-work DOCX. |
| `docs/Elite_Research_Execution_Plan.md` | Research plan and reviewer-risk checklist. |
| `AGENTS.md` | This file. |
| `memory.md` | Long-form project memory with full history and current state. |

---

## ⚙️ Current configuration

```python
N_PER_LANG = 5   # frozen v67: 15 proverbs total; scale to 15 per language after N=5 check
```

**Frozen v67 config:**
- Reverted v66 prompt hardening and length relaxation to v65 levels.
- Kept v65: option-level idiom blocklist, correct-option length outlier not counted as fallback, per-language NLI embedding guard, gold-meaning curation for all languages.
- Kept v66 local: `dup_replaced` excluded from fallback/partial status, reordered stable generator roster.
- LLM-based fallback distractor generator: disabled by default (`USE_LLM_FALLBACK = False`); available as optional ablation.

**Intended plan (post-v68 analysis):**
1. ✅ Freeze config and update documentation.
2. ✅ Regenerate notebook and push version 67/68.
3. ✅ Run Pilot 1 TEST N=5 on Kaggle (15 proverbs, $0.85).
4. ✅ Analyze N=5 quality and cost (see `kaggle_run_logs/v68/v68_detailed_analysis_report.md`).
5. ✅ Prepare v69 analysis plan, checklist, comparison scripts, and report template.
6. ~~Run v69 ablation~~ — attempted but blocked by OpenRouter budget limit.
7. ~~Scale to N=15 in v70~~ — attempted; v70 failed after 83 partial MCQs due to `403 Budget limit exceeded`.
8. **Pivot to paper-first:** v68 (180 MCQs, full audit, $0.85) is the production dataset.
9. **Run the paper-first notebook:** `jupyter execute paper_first_analysis_2026-06-22_10-42-02.ipynb` produces all tables/figures and the 60-item validation sample.
10. **Recruit native-speaker annotators** for the 60-item validation sample (20 per language; stratified by status and consensus correctness).
11. **Draft paper** around methodology + reproducible failure taxonomy (target EACL 2027 ARR).
12. **Renew OpenRouter budget** before any further Kaggle experiments.

---

## 🚀 How to run

1. Open Kaggle → Notebooks → Upload `openrouter_pilot_distractor_generation_test_nano_opus.ipynb`.
2. Add Kaggle Secret `OPENROUTER_API_KEY`.
3. Attach dataset `abrahamsunday123/full-data-complete`.
4. Run all cells.
5. Download the `/kaggle/working/openrouter_pilot1_test_output/` folder.

---

## 📊 Baseline — v58 Kaggle run (2026-06-20, N=1)

**Location:** `kaggle_run_logs/`  
**Full analysis:** `kaggle_run_logs/quality_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 45 |
| Total cost | **$0.2237 / $5.00** |
| Hard fallback rate | 0.0% ✅ |
| Active generators after preflight | 3 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **48.9%** ❌ (target <30%) |
| High-consensus-wrong rate | **22.2%** ❌ (target <10%) |
| Consensus accuracy | **60.0%** |
| Duplicate options | 2 ❌ |
| Correct-key balance | 12/11/11/11 ✅ |
| Partial + fallback | **28.9%** ❌ (target <15%) |

**Per-language consensus correctness:** English 72.7%, Arabic 63.6%, **Yoruba 40.0%** ❌

### v59 stepping-stone targets

| Gate | Target |
|---|---|
| Partial + fallback | <15% |
| High-consensus-wrong | <15% (then <10%) |
| Yoruba consensus correctness | ≥50% |
| Duplicate options | 0 |
| Cost | <$1.00 for N=1 |

> **Note:** Pilot 2 v3 (S1/S2 evaluator) is on hold until Pilot 1 TEST distractors clear the quality gates.

---

## 📊 Latest run — v61 Kaggle run (2026-06-20, N=1)

**Location:** `kaggle_run_logs/v61/`  
**Full analysis:** `kaggle_run_logs/v61/v61_detailed_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 36 |
| Total cost | **$0.1864 / $5.00** |
| Active generators after preflight | 3 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **47.2%** ❌ (target <30%) |
| High-consensus-wrong rate | **25.0%** ❌ (target <10%) |
| Consensus accuracy | **61.1%** |
| Duplicate options | 0 ✅ |
| Correct-key balance | 9/9/9/9 ✅ |
| Partial + fallback | **47.2%** ❌ (target <15%) |

**Per-language consensus correctness:** English 91.7% ✅, Arabic 58.3% ❌, **Yoruba 33.3%** ❌

## 🚨 Key findings from v61

1. **Sanitizers still rewrite ~47% of items.** Length relaxation and semantic widening helped slightly, but semantic/NLI/leak/length sanitizers continue to discard most model-generated distractors.
2. **Length_fallback label is misleading.** Many `length_fallback` items have acceptable length spreads but hit the ≥3-replacement threshold from semantic/NLI/leak sanitizers. The `adversarial-length-locked` and `adversarial-hard-negative` variants are the most brittle.
3. **English is too easy.** 91.7% consensus correctness drives perfect consensus up; distractors are not tempting enough.
4. **Yoruba remains broken.** Literal/awkward gold meanings, weak distractors, and culturally mismatched corpus fallbacks (some offensive) keep correctness at 33.3%.
5. **Fallback sampler can produce inappropriate content.** Some corpus-sampled Yoruba distractors contain vulgar or culturally jarring text.
6. **Cost is healthy.** $0.19 leaves plenty of headroom for extra LLM calls (e.g., fallback rewriting, Yoruba gold-meaning curation).

---

## 📊 Latest run — v63 Kaggle run (2026-06-21, N=1)

**Location:** `kaggle_run_logs/v63/`  
**Full analysis:** `kaggle_run_logs/v63/v63_detailed_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 36 |
| Total cost | **$0.1909 / $5.00** |
| Active generators after preflight | 3 ✅ (qwen/qwen3.7-max, google/gemini-2.5-flash, anthropic/claude-sonnet-4) |
| Benched generators | 1 ❌ (google/gemma-4-31b-it) |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **52.8%** ❌ (target <30%) |
| High-consensus-wrong rate | **33.3%** ❌ (target <10%) |
| Consensus accuracy | **55.6%** |
| Duplicate options | 0 ✅ |
| Correct-key balance | 9/9/9/9 ✅ |
| Partial + fallback | **36.1%** ❌ (target <15%) |

**Per-language consensus correctness:** English 100.0% ✅, Arabic 41.7% ❌, **Yoruba 25.0%** ❌

## 🚨 Key findings from v63

1. **Partial+fallback improved to 36.1%.** The v62 length/leak relaxations worked; `length_fallback` fell to 8.3% and mean `fallback_count` dropped to 0.75.
2. **HCW and perfect consensus both worsened.** HCW rose to 33.3% and perfect consensus to 52.8%. The distractors are now attractive enough for auditors to agree, but they often agree on the wrong answer.
3. **English remains too easy.** 100% consensus correctness with 10 perfect-consensus items means English distractors are still not tempting enough.
4. **Arabic and Yoruba are the HCW drivers.** Arabic 6/12 HCW; Yoruba 6/12 HCW. Several distractors are generic English idioms that the blocklist missed, or near-paraphrases of the correct meaning that NLI did not flag.
5. **NLI barely fired.** Only 5 NLI replacements across 36 items, suggesting the embedding guard (0.55) is suppressing legitimate paraphrase flags.
6. **Yoruba curation ran but did not lift correctness.** Raw outputs confirm the literal gloss was rewritten, but the new meaning is still close to many distractors.
7. **`google/gemma-4-31b-it` was benched.** Dynamic substitution promoted `anthropic/claude-sonnet-4`, keeping 3 active generators.

---

## 📊 Latest run — v65 Kaggle run (2026-06-21, N=1)

**Location:** `kaggle_run_logs/v65/`  
**Full analysis:** `kaggle_run_logs/v65/v65_detailed_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 36 |
| Total cost | **$0.1879 / $5.00** |
| Active generators after preflight | 3 ✅ (qwen/qwen3.7-max, google/gemini-2.5-flash, anthropic/claude-sonnet-4) |
| Benched generators | 1 ❌ (google/gemma-4-31b-it) |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **41.7%** ❌ (target <30%) |
| High-consensus-wrong rate | **11.1%** ❌ (target <10%, but within step target <15%) |
| Consensus accuracy | **63.9%** |
| Duplicate options | 0 ✅ |
| Correct-key balance | 8/10/7/11 (acceptable) |
| Partial + fallback | **36.1%** ❌ (target <15%) |

**Per-language consensus correctness:** English 100.0% ✅, Arabic 50.0% ❌, **Yoruba 41.7%** ❌

## 🚨 Key findings from v65

1. **HCW dropped to 11.1%.** Option-level blocklist + tighter Arabic/Yoruba NLI guard removed the confident-wrong fallback items.
2. **Partial+fallback improved slightly to 36.1%.** Parse-fallbacks are gone (0 vs 4 in v64), but 9 partials and 4 length-fallbacks remain.
3. **English remains trivially easy.** 100% consensus correct with near-perfect consensus; distractors are generic reversals or unrelated idioms.
4. **Yoruba correctness regressed to 41.7%.** Hard-negative distractors are structurally parallel analogies that auditors prefer over the gourd/farmer key.
5. **Generator churn persists.** `google/gemma-4-31b-it` was benched mid-run and replaced by `anthropic/claude-sonnet-4`, adding roster noise.

---

## 📊 Latest run — v66 Kaggle run (2026-06-21, N=1)

**Location:** `kaggle_run_logs/v66/`  
**Full analysis:** `kaggle_run_logs/v66/v66_detailed_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 36 |
| Total cost | **$0.1754 / $5.00** |
| Active generators after preflight | 3 ✅ (qwen/qwen3.7-max, google/gemma-4-31b-it, google/gemini-2.5-flash) |
| Benched generators | 0 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **55.6%** ❌ (target <30%) |
| High-consensus-wrong rate | **22.2%** ❌ (target <10%) |
| Consensus accuracy | **69.4%** |
| Duplicate options | 0 ✅ |
| Correct-key balance | 8/9/9/10 (acceptable) |
| Partial + fallback | **50.0%** ❌ (target <15%) |

**Per-language consensus correctness:** English 100.0% ✅, Arabic 58.3% ❌, **Yoruba 50.0%** ✅

## 🚨 Key findings from v66

1. **Prompt hardening backfired.** Models still produced generic reversals and unrelated idioms; closer-to-correct attempts were caught by NLI and replaced by low-quality corpus fallbacks.
2. **NLI replacements doubled** (16 vs 8 in v65), driving partial items up from 9 to 16 and HCW from 11.1% to 22.2%.
3. **Length relaxation did not help net partial+fallback.** Length_fallback fell from 4 to 2, but items became partial instead.
4. **Generator roster stabilised.** No mid-run substitutions, confirming the reordered pool works.
5. **English remains 100% consensus correct.** The prompt changes were not enough to make English distractors difficult.
6. **Core diagnosis:** the corpus-based fallback sampler is the bottleneck. Replacing it with an LLM-generated distractor is now the highest-leverage fix.

---

## 🔧 v2 fixes already implemented (before 2026-06-17 smoke test)

- Replaced unreliable `openai/gpt-5` auditor with `anthropic/claude-sonnet-4`.
- Standardised vote extraction to uppercase `A-D` and integer `1/0` hits.
- Dropped `baseline` and `misconception-based` prompts; added `adversarial-length-locked` and `adversarial-hard-negative`.
- Added self-critique loop infrastructure with `CRITIC_MODEL`.
- Hardened corpus fallback sampler (rejects broken English / duplicates).
- Balanced correct-key distribution via round-robin counter.
- Deterministic tie-breaking in consensus.
- Added human-annotation export and **10 PNG visualisations**.

## 🔧 v2.1 fixes implemented (after 2026-06-17 smoke test)

- **Self-critique:** `CRITIC_MODEL` changed from invalid `google/gemini-2.5-flash-preview` to valid `anthropic/claude-3.5-haiku`.
- **Audit committee:** starters are now `llama-3.3-70b`, `mistral-small-3.2-24b`, `gemma-3-27b-it`, `qwen/qwen3-32b`; removed unreliable `claude-sonnet-4` from starters.
- **Generator substitutes:** replaced high-fallback `qwen/qwen3-14b`, `llama-4-scout`, `openai/gpt-4.1` with `gemini-2.5-pro`, `gemini-2.5-flash`, `gpt-4.1-mini`, `gpt-4.1-nano`.
- **Meta-text rejection:** added `has_meta_text()` and treat markdown headings / instruction leaks as parse failures.
- **Length check:** now uses median length of all four options instead of only the correct meaning, reducing false partials.
- **Vote extraction:** hardened to handle `**A**`, `(B)`, `A)`, `{"answer":"C"}`, and `Choice: D` patterns.
- **Resume-state bug:** `save_state()` now passes `generation_done` / `audit_done` flags correctly.
- **Prompt catalog:** replaced parser-confusing `few-shot-predictive` variant with `adversarial-contrastive`.

## 🔧 v2.2 fixes implemented (after 2026-06-19 smoke test)

- **Audit committee:** removed `qwen/qwen3-32b` (97.8% missing votes) and `openai/gpt-4o-mini` (weak substitute). Starters are now `llama-3.3-70b`, `mistral-small-3.2-24b`, `gemma-3-27b-it`, `anthropic/claude-3.5-haiku`. Substitutes are `deepseek/deepseek-v3.2` and `amazon/nova-lite-v1`.
- **Generator cost cut:** replaced expensive `anthropic/claude-opus-4.8` ($5/$25 per 1M) with cheaper `anthropic/claude-sonnet-4` ($3/$15 per 1M) in the generator pool.
- **Self-critique:** disabled (`USE_SELF_CRITIQUE = False`) because it triggered rewrites on every item without improving shortcut-resistance.
- **Yoruba hardening:** added cultural-context instruction to the generation prompt and a blocklist validator that rejects generic English idioms/proverbs (e.g., "a bird in the hand", "the apple does not fall far from the tree") as Yoruba distractors.
- **Notebook regenerated** from updated source.

## 🔧 v2.3 / Pilot 2 v3 fixes implemented (June 20, 2026)

- **EOL auditor replaced:** `anthropic/claude-3.5-haiku` is EOL on OpenRouter/AWS Bedrock (404). It has been replaced by `deepseek/deepseek-v3.2` in both Pilot 1 TEST and Pilot 2 v3.
- **Pilot 2 position bias fixed:** split the shared `POSITION_COUNTER` into independent `S1_POSITION_COUNTER` and `S2_POSITION_COUNTER`; `assemble_mcq()` now accepts a `counter_name` argument.
- **Pilot 2 generator rotation fixed:** the run now round-robins across `generator_pool.active` instead of always using `active[0]`.
- **Re-keyed existing Pilot 2 data:** `rekey_s1_s2_pilot_v1.py` produced balanced A-D versions of the June 19 CSVs (`mcqs_s1_rekeyed.csv`, `mcqs_s2_rekeyed.csv`).
- **Parser hardening:** `extract_choice()` in Pilot 2 now accepts `answer = X` and `{"answer": "X"}` patterns.
- **Yoruba guard extended:** S2 generation now also rejects generic English idioms for Yoruba proverbs.
- **Meta-text rejection strengthened:** `_META_PATTERNS` expanded to catch markdown italic/inline code and stage labels such as `step 1`, `final output`, `selected options`.
- **Yoruba blocklist expanded:** ~120 generic English idioms/proverbs with punctuation-insensitive fuzzy matching.
- **Working-tree cleanup:** stale backups, legacy v3/v4.3.6/Groq scripts, old local outputs, logs, and duplicate zips/CSVs archived to `.archive/`.

## 🔧 v59 fixes implemented (2026-06-19)

- **P0 — Post-processing hardening:**
  - Expanded `_GENERIC_ENGLISH_IDIOM_BLOCKLIST` with v58 leakages (`east or west home is best`, `go big or go home`, `make a rod for...`, etc.).
  - Added `has_correct_meaning_leak()` with leading-phrase echo + 80% token-overlap detection.
  - Converted duplicate detection to `repair_duplicate_options()` with near-duplicate (Jaccard > 0.5 / token overlap ≥ 0.85) repair and uniqueness enforcement.
  - Hardened fallback sampler with length-ratio filtering, exclude sets, and weighted-random selection to avoid repeated collisions.
  - Relaxed `SEMANTIC_DISTANCE_BAND` to default max 0.82 / Yoruba max 0.85.
  - Updated prompt constraints to ban well-known English idioms and near-paraphrases.
- **P1 — NLI paraphrase filter:**
  - Lazy-loaded `cross-encoder/nli-deberta-v3-xsmall`.
  - Added `nli_paraphrase_filter_ok()` / `_sanitize_nli_paraphrases()` rejecting distractors with NLI entailment > 0.60 **and** embedding similarity > 0.55.
- **P2 — Evaluation additions:**
  - Added `compute_distractor_metrics()` writing `pilot1_test_distractor_metrics.csv` and summary JSON.
  - Added `nli_replaced` and `duplicate_options` tracking.
  - Added with-proverb baseline audit (`pilot1_test_with_proverb_baseline.csv`).
  - Updated human-annotation export with generation status, fallback count, and consensus info.
- **Infrastructure:**
  - Local tests: `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.
  - Notebook regeneration script updated with current roster/config.

## 🔧 v60 fixes implemented (2026-06-20)

- **Converted `has_correct_meaning_leak()` from hard rejection to sanitizer:**
  - Added `_is_correct_meaning_leak()` and `_sanitize_correct_meaning_leak()`.
  - The filter now replaces only the leaking distractor(s) with a fallback sample instead of throwing away the whole generated option set.
  - `generate_options()` now calls the sanitizer and counts replacements in `fallback_count` / `leak_replaced`.
- **Fixed generator benching for soft failures:**
  - `ModelPool` now distinguishes hard failures (weight ≥ 2, threshold 2) from soft failures (weight 1, threshold 5).
  - High-quality starters are no longer benched after only 2 parse/meta/idiom/leak quality-filter misses.
- **Pushed version 60 to Kaggle:** `abrahamsunday123/mcq-pass-shortcut`.

## 🔧 v61 fixes implemented (2026-06-20)

- **Relaxed length check:** `LENGTH_CHECK_THRESHOLD` 0.20 → 0.30 (±20% → ±30%).
- **Widened semantic-distance band:** default max 0.82 → 0.85; Yoruba max 0.85 → 0.88.
- **Removed `adversarial-contrastive` variant:** it produced near-paraphrases that the sanitizers rewrote into fallback-heavy `length_fallback` items (0 generated, 9/9 length_fallback in v60).
- **Updated prompt variants JSON:** all variant templates and shared constraints now say ±30% instead of ±20%.
- **Pushed version 61 to Kaggle:** `abrahamsunday123/mcq-pass-shortcut`.

## 🔧 v62 fixes implemented (2026-06-21)

Recommended A+B+E+F intervention applied:

- **A — Smarter length parity:**
  - `LENGTH_CHECK_THRESHOLD` 0.30 → 0.35 (±30% → ±35%).
  - Added `LENGTH_RELAXED_THRESHOLD = 0.45`: if all four options are within ±45% of each other, the whole set is accepted without replacing outliers.
  - `passes_length_check()` now accepts an optional `relaxed_threshold`.
  - Status logic now labels `length_fallback` only when `length_replaced >= 2`, making the label more meaningful.
- **B — Per-language leak threshold:**
  - Added `LEAK_THRESHOLD_BY_LANGUAGE`: English 0.90, Arabic/Yoruba 0.80.
  - `generate_options()` passes the language-specific threshold to `_sanitize_correct_meaning_leak()`.
- **C — Per-language semantic band (included as a supporting change):**
  - `SEMANTIC_DISTANCE_BAND` now has `english` max 0.88, `default` max 0.86, `yoruba` max 0.90.
- **E — Yoruba gold-meaning curation:**
  - Added `curate_yoruba_meaning()` using `openai/gpt-4.1-nano` to rewrite literal/awkward Yoruba glosses into natural English.
  - Results are cached per proverb so multiple generators/variants reuse the same curation.
  - RAW outputs now record `original_meaning` and `curated_meaning`.
- **F — Fallback quality guard:**
  - Added `_FALLBACK_OFFENSIVE_BLOCKLIST` and `_is_offensive_or_inappropriate()`.
  - `semantically_distinct_negative_sample()` rejects offensive/vulgar corpus fallbacks at every selection pass.
- **Prompt catalog:** updated shared constraints and all variant templates to ±35% (with ±45% relaxed all-within).
- **Notebook regenerated** from updated source and **pushed version 63** to `abrahamsunday123/mcq-pass-shortcut` (v62 contained the code changes; v63 corrected the markdown cell copy).
- **Local tests:** `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

---

## v64 fixes implemented (2026-06-21)

Recommended A+B+C+D follow-up to v63:

- **A — Curate all gold meanings.** Renamed `curate_yoruba_meaning()` to `curate_gold_meaning()` and applied it to English, Arabic, and Yoruba. The curator uses `openai/gpt-4.1-nano` and language-specific instructions:
  - Yoruba: preserve the neckless/collarless gourd, farmer, and tying/binding image.
  - Arabic: preserve the specific moral/social situation; avoid generic English idioms.
- **B — Expanded generic-English idiom blocklist.** Added v63 leakages: `People in glass houses...`, `The proof is in the pudding`, `Speech is silver, silence is gold`, `Silence is golden`, `Mind your own business`, `Add fuel to the flames`, `Better suffer ill than do ill`, `Experience is the best teacher`, etc.
- **C — Language-specific NLI embedding guard.** Added `NLI_EMBEDDING_GUARD_BY_LANGUAGE`: Arabic/Yoruba 0.45, default 0.55. This lets the NLI filter catch more near-paraphrase distractors in the low-resource languages without increasing false positives in English.
- **D — Improved Yoruba curation prompt.** Explicitly instructs the curator to keep the concrete gourd/farmer/bind imagery.
- **CSV metadata:** `pilot1_test_generated_mcqs.csv` now records `original_meaning` and `curated_meaning`; `correct_meaning` is the curated version actually used for generation/audit.
- **Notebook regenerated** from updated source and **pushed version 64** to `abrahamsunday123/mcq-pass-shortcut`.
- **Local tests:** `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

---

## v65 fixes implemented (2026-06-21)

Recommended A+B+C follow-up to v64 analysis:

- **A — Option-level idiom blocklist.** `has_generic_english_idiom()` now accepts `skip_correct_option=True`. `_sanitize_blocked_idioms()` replaces only the distractors that contain a generic English idiom instead of rejecting the whole MCQ. This fixes the v64 Arabic parse-fallbacks where the curated gold meaning itself was "Charity begins at home."
- **B — Do not count correct-option length outliers as fallbacks.** The correct meaning is still checked for length parity, but a correct-option outlier is recorded as `correct_length_outlier` rather than added to `length_replaced` / `fallback_count`. This prevents otherwise-good MCQs from being labelled `length_fallback` just because the key is longer than the distractors.
- **C — Raise English NLI embedding guard to 0.58.** Looser than the default 0.55 so that more subtle near-paraphrase distractors survive for English proverbs, lowering the v64 91.7% consensus-correct rate without letting through true paraphrases.
- **Raw-output metadata:** `RAW_OUTPUTS` now records `blocklist_replaced` and `correct_length_outlier` per generation attempt.
- **Notebook regenerated** from updated source and **pushed version 65** to `abrahamsunday123/mcq-pass-shortcut`.
- **Local tests:** `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

---

## v66 fixes implemented (2026-06-21)

Quick v66 bundle selected after v65 forensic deep dive:

- **A — Exclude `dup_replaced` from fallback/partial status.** `fallback_count` now counts only length/leak/semantic/NLI replacements. Duplicate repair is reported separately but no longer pushes items into `partial` or `length_fallback`.
- **B — Relax length parity.** `LENGTH_CHECK_THRESHOLD` 0.35 → 0.45; `LENGTH_RELAXED_THRESHOLD` 0.45 → 0.55, to reduce false length-fallbacks.
- **C — Harden prompts against generic reversals.** Added explicit constraints to all variants: distractors must be plausible misreadings of the target proverb, not generic life advice, obvious opposites, or unrelated English idioms.
- **D — Stabilise generator roster.** Reordered generator pool so primary substitutes are `google/gemini-2.5-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`; `anthropic/claude-sonnet-4` is now an emergency-only substitute.
- **Notebook regenerated** from updated source and **pushed version 66** to `abrahamsunday123/mcq-pass-shortcut`.
- **Local tests:** `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

---

## v67 options after v66 regression

v66 moved gates in the wrong direction. The diagnosis is that the corpus-based fallback sampler is the bottleneck: every NLI/length/duplicate replacement pulls a random meaning from other proverbs, which is either too easy or a confident-wrong trap.

Candidate v67 bundles:

- **v67a — Revert + fallback-generator (recommended):** Revert v66 prompt/length changes to the v65 baseline, keep the `dup_replaced` bookkeeping and the reordered generator pool, and replace the corpus fallback sampler with an LLM-based distractor generator (`gpt-4.1-nano` or `gemini-2.5-flash`) that produces a single, length-matched, proverb-specific hard negative on demand.
- **v67b — Fallback-generator only:** Keep current v66 prompts/length and add the LLM-based fallback generator. Isolates the fallback effect but keeps the worse v66 prompt behaviour.
- **v67c — Template-based fallback:** Replace corpus sampling with deterministic perturbation templates (change agent, scope, causal direction, modality). Cheaper than an LLM call but may be repetitive.

**Next action:** Choose one of the above, implement, regenerate notebook, and push version 67.

---

## 📊 Latest run — v68 Kaggle run (2026-06-22, N=5)

**Location:** `kaggle_run_logs/v68/`  
**Full analysis:** `kaggle_run_logs/v68/v68_detailed_analysis_report.md`

| Metric | Value |
|---|---|
| Sample | 15 proverbs (5 English, 5 Arabic, 5 Yoruba) |
| MCQs generated | **180** (3 generators × 4 variants × 15 proverbs) |
| Total cost | **$0.8539 / $5.00** |
| Active generators after preflight | 3 ✅ (`qwen/qwen3.7-max`, `google/gemma-4-31b-it`, `google/gemini-2.5-flash`) |
| Benched generators | 0 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **41.7%** ❌ (target <30%) |
| High-consensus-wrong rate | **27.8%** ❌ (target <10%) |
| Consensus accuracy | **56.7%** |
| Duplicate options | 0 ✅ |
| Correct-key balance | 45/45/45/45 ✅ |
| Partial + fallback | **43.9%** ❌ (target <15%) |
| Hard fallback (`length_fallback`) | **16.1%** ❌ (target <5%) |

**Per-language consensus correctness:** English 65.0%, Arabic 53.3%, Yoruba 51.7%

**Per-language HCW (≥3/4 auditors agree on wrong answer):** English 18.3%, Arabic 31.7%, Yoruba 33.3%

## 🚨 Key findings from v68

1. **HCW jumped to 27.8% at N=5.** Up from 11.1% in v65 (N=1) and 22.2% in v66 (N=1). Corpus fallbacks frequently attract auditor consensus.
2. **Partial+fallback remains 43.9%.** Far above the 15% target; mean 0.99 corpus replacements per MCQ.
3. **NLI and leak filters are the dominant rewriters.** Mean 0.36 NLI replacements and 0.35 leak replacements per MCQ; length is only 0.15.
4. **Corpus fallback sampler is the confirmed bottleneck.** 43.9% of MCQs needed fallback replacements, and the fallbacks drive confident-wrong consensus.
5. **English is still too easy.** 65.0% consensus accuracy and 45.0% perfect consensus; distractors are not tempting enough.
6. **Arabic and Yoruba are fragile.** Both meet the ≥50% correctness gate only barely; HCW is 31.7% and 33.3% respectively.
7. **`adversarial-hard-negative` is the most damaged variant.** Only 26.7% fully generated, 42.2% `length_fallback`, 40.0% HCW.
8. **`google/gemma-4-31b-it` is the strongest generator.** 65.0% accuracy, 35.0% HCW, 66.7% fully generated.
9. **Roster is stable.** 0 benched generators, 0 missing auditor votes.

## v67/v68 fixes implemented (2026-06-21–22)

- **Frozen v67 config:** reverted v66 prompt/length changes to v65 levels; kept option-level blocklist, correct-option length outlier fix, `dup_replaced` exclusion, per-language NLI guard, gold curation for all languages, stable generator roster.
- **N=5 scaling:** bumped `N_PER_LANG` from 1 to 5.
- **LLM fallback generator retained but disabled:** `USE_LLM_FALLBACK = False` in v68; available for v69 ablation.
- **Kaggle push+run automation:** `trigger_kaggle_run.py` uses `ApiSaveKernelRequest` with `kernel_execution_type = SAVE_AND_RUN_ALL`.
- **Notebook regenerated** from updated source and **pushed version 68** to `abrahamsunday123/mcq-pass-shortcut`.
- **Local tests:** `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

## v69 ablation implementation (2026-06-22)

Enabled the previously-disabled LLM-based fallback distractor generator for the v69 Kaggle run:

- **`USE_LLM_FALLBACK = True`**; `FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"`.
- **Wired context functions:** `_set_llm_fallback_context(proverb, variant["name"])` and `_clear_llm_fallback_context()` are now called inside `generate_options()` so the fallback generator is proverb-aware and variant-aware.
- **Fixed broken NLI check in fallback:** replaced the single-direction, malformed-probe check with symmetric forward/backward entailment, identical to the main pipeline.
- **Added missing filters:** correct-meaning leak guard and meta-text guard; generic-English idiom/offensive guards were already present. Fallback now applies the same filter stack as generator outputs.
- **Explicit reproducibility:** `openrouter_chat()` accepts an optional `temperature` parameter; the fallback generator calls it with `temperature=0.0`.
- **Recursion safety:** both the missing-context guard and the all-attempts-failed path in `generate_llm_fallback_distractor()` call `semantically_distinct_negative_sample(..., use_llm=False)` to prevent LLM↔corpus recursion.
- **Observability:** added `_LLM_FALLBACK_USED` / `_LLM_FALLBACK_REJECTED` counters and `version` / `use_llm_fallback` / `fallback_generator_model` fields to `pilot1_test_summary.json`.
- **Notebook regenerated** from updated source and **pushed version 69** to `abrahamsunday123/mcq-pass-shortcut`; run triggered via `trigger_kaggle_run.py`.
- **Local validation:** `python -m py_compile` and `test_integration.py` pass.

## v69 plan

Run focused ablation with `USE_LLM_FALLBACK = True`, `N_PER_LANG = 5`. Success gates: HCW <15%, partial+fallback <30%, cost <$1.50. If passed, freeze and scale to N=15 in v70. If failed or marginal, use v68/v69 as production data and move to human validation + paper draft.

---

## ✅ Remaining blockers before scaling to N=15

| Priority | Item | Status |
|---|---|---|
| **P0** | Duplicate-repair collision bug | ✅ Fixed |
| **P0** | Fallback sampler determinism/collisions | ✅ Weighted random selection + exclude sets |
| **P0** | NLI false-positive suppression | ✅ Embedding guard 0.55 (English 0.58) |
| **P0** | Correct-meaning leak filter too blunt | ✅ Converted to sanitizer in v60 |
| **P0** | Generator benching after 2 soft failures | ✅ Soft threshold raised to 5 in v60 |
| **P0** | Length check too strict | ✅ v65: correct option no longer counted as fallback |
| **P0** | `adversarial-contrastive` variant broken | ✅ Removed in v61 |
| **P0** | Idiom blocklist over-firing on correct option | ✅ Fixed in v65 |
| **P1** | Reduce confident-wrong consensus | ❌ v68 N=5: 27.8% HCW; corpus fallbacks are the driver |
| **P1** | Improve Yoruba consensus correctness | ⚠️ v68 N=5: 51.7% (meets ≥50% gate but fragile) |
| **P1** | Lower partial+fallback rate | ❌ v68 N=5: 43.9%; corpus fallback sampler is the bottleneck |
| **P1** | English too easy | ❌ v68 N=5: 65.0% consensus correct, 45.0% perfect consensus |
| **P1** | Generator roster churn | ✅ Stabilised in v68 (0 benched) |
| **P1** | Fallback sampler quality | ❌ Corpus sampler confirmed main blocker; v69 LLM fallback ablation next |
| **P2** | Self-critique redesign | 🔲 Disabled; reconsider only after P1 gates pass |
| **P2** | Scale to N=5 / N=15 | 🔄 N=5 complete; N=15 blocked until v69 ablation passes |
| **P2** | Human validation subset (60 MCQs, 20/language) | 🔄 Planned after final N=5 or N=15 run |
| **P2** | Paper draft around methodology + failure taxonomy | 🔄 Begin drafting in parallel with v69 |

---

## 🧭 Paper-first scaling strategy

We are stopping the N=1 prompt-tuning loop. The frozen v67 config gives us the best v65-quality results with a stable roster. The paper will be framed around:

1. **Methodology:** hardened dynamic-generator + blind options-only audit pipeline.
2. **Cross-lingual findings:** S1 vs S2 difficulty, per-language gaps (especially Yoruba), position bias, model-family exploitation, API fragility.
3. **Reproducible failure taxonomy:** partial+fallback, high-consensus-wrong, length/leak/NLI replacements, corpus fallback limitations.
4. **Human validation:** 60-item subset from the N=15 run, 2–3 annotators, IAA reported.
5. **Transparent limitations:** corpus fallback sampler and options-only audit are documented as deliberate design choices, not hidden weaknesses.

Scaling budget:
- N=5 per language → 15 proverbs, target ~$0.90.
- N=15 per language → 45 proverbs, target ~$2.70.
- Both remain under the $5.00 cost cap.

---

## 🎯 Success criteria for the N=5 run

| Gate | Target |
|---|---|
| Hard fallback rate | < 5% |
| Partial + fallback rate | < 15% |
| Active generators/auditors after preflight | ≥ 3 each |
| Perfect consensus rate | < 30% |
| High-consensus-wrong rate | < 10% |
| Per-language consensus correctness | ≥ 50% each (especially Yoruba) |
| Duplicate options | 0% |
| Correct-key balance | ~25% each for A-D |
| Cost | Under $5.00 |

> **Note:** We no longer require every gate to be green at N=1 before scaling. The goal is to confirm the frozen v67 config is stable at N=5, then collect interpretable per-language statistics at N=15 and validate with human annotators.

---

## 📓 OpenRouter Pilot 2 v3 — S1/S2 evaluator notebook

**Notebook:** `openrouter_pilot_s1_s2_evaluator.ipynb`  
**Source:** `openrouter_pilot_s1_s2_evaluator_v3.py`  
**Converter:** `convert_pilot2_to_notebook.py`

This notebook now shares the hardened infrastructure from the Pilot 1 TEST distractor-generation notebook.

| Item | Status |
|---|---|
| Source file | ✅ `openrouter_pilot_s1_s2_evaluator_v3.py` (≈1,780 lines) |
| Notebook regenerated | ✅ `openrouter_pilot_s1_s2_evaluator.ipynb` (4 cells) |
| Local mocked test | ✅ `python test_pilot2_local.py` passes |
| Kaggle run | ✅ Completed 2026-06-19 (N=10); infrastructure PASS, quality FAIL, P0 bugs found |

**What it does:**
- Loads the same raw data as Pilot 1 TEST (`actual_data/cleaned` fallback, Kaggle dataset `abrahamsunday123/full-data-complete`).
- Samples `N_PER_LANG = 10` proverbs per language (30 total; lower for smoke tests).
- Generates **fresh S1** (proverb → 4 English meanings) and **fresh S2** (English meaning → 4 source-language proverbs) using a dynamic generator pool.
- Audits both strategies with a dynamic, **disjoint** audit pool.

**Model pools:**
- **Generator starters:** `google/gemini-2.5-pro`, `qwen/qwen3.5-397b-a17b`, `anthropic/claude-sonnet-4`
- **Generator substitutes:** `google/gemma-4-31b-it`, `deepseek/deepseek-v4-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`
- **Note:** `anthropic/claude-opus-4.8` was intentionally dropped from both pilot pools for cost; `claude-sonnet-4` is the cheaper Anthropic stand-in ($3/$15 per 1M vs $5/$25).
- **Audit starters:** `meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-small-3.2-24b-instruct`, `google/gemma-3-27b-it`, `deepseek/deepseek-v3.2`
- **Audit substitutes:** `amazon/nova-lite-v1`

**Guards implemented:**
- Live OpenRouter catalog filter + cheap echo preflight.
- Hardened `openrouter_chat` with 400/422 fallbacks and reasoning-family token limits.
- `CostTracker` with live price refresh and `$5` hard cap.
- Robust `parse_options` / `extract_choice` + parser self-test.
- Meta-text rejection, length parity (±20%), duplicate detection.
- S1: optional sentence-transformer paraphrase guard (threshold 0.85) + Yoruba English-idiom blocklist.
- S2: source-language retention, no duplicates, no minor rewordings, ASCII-ratio guard for non-English.
- Corpus-based fallbacks for both strategies.
- Resume state saved to `pilot2_state.json`; incremental CSV flushes.

**Outputs:**
- `mcqs_s1.csv`, `mcqs_s2.csv`
- `pilot2_eval_results.csv`
- `pilot2_summary.json`
- `pilot2_state.json`
- `pilot2_raw_outputs.csv`

**Next steps (P0 fixes first):**
1. Replace EOL `anthropic/claude-3.5-haiku` in both pilot sources with a verified active Anthropic model (or promote `deepseek/deepseek-v3.2`).
2. Fix `assemble_mcq()` in Pilot 2 v3 to use a shared global position counter across S1 and S2.
3. Fix Pilot 2 v3 generator selection to actually rotate across active generators.
4. Re-key the existing `S1_S2_pilot_v1/mcqs_s1.csv` and `mcqs_s2.csv` so the data is not wasted.
5. Regenerate both notebooks and re-run local mocked tests.
6. Re-run Pilot 1 N=1 and Pilot 2 N=2–3 smoke tests on Kaggle.
7. Only scale after all gates pass.

---

## 📓 Groq S1 + S2 main pipeline (side note)

The older Groq-based pipeline (`kaggle_full_pipeline_notebook.py` / `.ipynb`) was also hardened with a semantic paraphrase guard, but it is **not** the pilot notebook the user asked about. Re-run it only if you need the legacy S1/S2 baseline.

---

## 🧠 MCP memory

Check these MCP memory entities for full history:
- `ProverbGap MCQ`
- `OpenRouter Generation Pilot Kaggle Run 2026-06-19`
- `OpenRouter S1/S2 Pilot Kaggle Run 2026-06-19`
- `P0 Fix Cycle 2026-06-20`
- `Blind Shortcut Audit Literature Review`
- `Stale Markdown Cleanup 2026-06-19`
- `Dynamic Model Substitution`
- `Elite Research Execution Plan`
- `OpenRouter Model Selection Mistakes`
