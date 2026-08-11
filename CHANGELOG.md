# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Publication-ready GitHub community documentation (README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG)
- Paper-first analysis notebook and 60-item human-validation sample generation
- Reviewer response documents for EACL 2027 ARR

### Changed
- Pivoted from scale-first to paper-first workflow: v68 N=5 dataset is now the production dataset
- Human-validation protocol updated to 60-item stratified subset (20 per language)

### Known Issues
- Corpus fallback sampler remains the primary quality bottleneck (43.9% partial+fallback, 27.8% HCW)
- OpenRouter budget limit blocked v69 LLM-fallback ablation and v70 N=15 scaling

---

## [v68] - 2026-06-22

### Added
- v68 N=5 Kaggle run: **180 MCQs** generated from 15 proverbs (5 per language)
- Frozen v67 configuration with stable generator roster
- Production dataset release: `data/production/v68/`
- Wilson confidence intervals and paired statistical comparisons (McNemar, Wilcoxon, bootstrap)
- 10 PNG visualizations for paper figures

### Changed
- Generator roster stabilized: 0 benched generators across the full run
- Correct-key balance achieved: 45/45/45/45 (perfect A–D parity)
- Per-language consensus correctness: English 65.0%, Arabic 53.3%, Yoruba 51.7%
- Cost: **$0.85** for N=5 (target <$1.00)

### Fixed
- P0 duplicate-repair collision bug
- P0 fallback sampler determinism and collisions
- P0 NLI false-positive suppression via per-language embedding guard
- P0 correct-meaning leak filter too blunt (converted to sanitizer)
- P0 generator benching after soft failures (threshold raised to 5)

### Known Issues
- Perfect consensus rate: 41.7% (target <30%)
- High-consensus-wrong rate: 27.8% (target <10%)
- Partial + fallback rate: 43.9% (target <15%)
- Hard fallback (`length_fallback`) rate: 16.1% (target <5%)

---

## [v67] - 2026-06-21

### Added
- Frozen v67 config for stable N=5 scaling
- `USE_LLM_FALLBACK = False` flag retained for future ablation
- Notebook regeneration and Kaggle push automation (`trigger_kaggle_run.py`)

### Changed
- Reverted v66 prompt hardening and length relaxation to v65 levels
- Kept v65 option-level idiom blocklist, correct-option length outlier fix, and `dup_replaced` exclusion
- Kept v66 stable generator roster reordering

### Fixed
- Stabilized generator roster: `anthropic/claude-sonnet-4` demoted to emergency-only substitute

---

## [v66] - 2026-06-21

### Added
- v66 N=1 Kaggle run: 36 MCQs from 3 proverbs (1 per language)
- Adversarial prompt hardening against generic reversals

### Changed
- Length parity relaxed: `LENGTH_CHECK_THRESHOLD` 0.35 → 0.45; `LENGTH_RELAXED_THRESHOLD` 0.45 → 0.55
- Prompt constraints hardened to ban generic life advice and obvious opposites
- Generator roster reordered for stability

### Known Issues
- Partial + fallback rate rose to 50.0%
- NLI replacements doubled (16 vs 8 in v65), driving partial items up and HCW to 22.2%
- Prompt hardening backfired: models produced generic reversals caught by NLI and replaced by low-quality corpus fallbacks

---

## [v65] - 2026-06-21

### Added
- v65 N=1 Kaggle run: 36 MCQs from 3 proverbs
- Option-level idiom blocklist (sanitizes only offending distractors)
- Correct-option length outlier tracking (`correct_length_outlier` status)

### Changed
- English NLI embedding guard raised to 0.58 (looser than default 0.55)
- Correct-option length outliers no longer counted as `fallback_count`
- Gold-meaning curation applied to all languages (English, Arabic, Yoruba)

### Fixed
- Idiom blocklist over-firing on correct option (v64 bug where curated gold meaning "Charity begins at home" triggered blocklist rejection)
- NLI false-positive suppression via per-language embedding guard

### Known Issues
- Partial + fallback rate: 36.1% (target <15%)
- Perfect consensus rate: 41.7% (target <30%)
- High-consensus-wrong rate: 11.1% (target <10%, within step target <15%)

---

## [v64] - 2026-06-21

### Added
- Gold-meaning curation for all languages (`curate_gold_meaning()`)
- Expanded generic-English idiom blocklist with v63 leakages
- Per-language NLI embedding guard (`NLI_EMBEDDING_GUARD_BY_LANGUAGE`)

### Changed
- Yoruba curation prompt improved to preserve concrete gourd/farmer/bind imagery
- `pilot1_test_generated_mcqs.csv` now records `original_meaning` and `curated_meaning`

### Known Issues
- 9 parse-fallback items where correct option triggered blocklist rejection
- 91.7% consensus correctness in English (too easy)
- Yoruba consensus correctness regressed to 41.7%

---

## [v63] - 2026-06-21

### Added
- v63 N=1 Kaggle run: 36 MCQs from 3 proverbs
- Parse-fallback tracking and diagnosis

### Changed
- Length check relaxed to ±35% with ±45% relaxed all-within threshold
- Per-language leak thresholds (English 0.90, Arabic/Yoruba 0.80)
- Yoruba gold-meaning curation (`curate_yoruba_meaning()`) with caching
- Fallback quality guard: offensive/vulgar corpus fallback rejection

### Known Issues
- Partial + fallback rate: 36.1%
- High-consensus-wrong rate: 33.3%
- NLI barely fired (only 5 replacements across 36 items)
- `google/gemma-4-31b-it` benched mid-run; replaced by `anthropic/claude-sonnet-4`

---

## [v62] - 2026-06-21

### Added
- Length parity A+B+E+F intervention bundle
- `LENGTH_RELAXED_THRESHOLD` for all-within acceptance
- Per-language leak threshold (`LEAK_THRESHOLD_BY_LANGUAGE`)
- `_FALLBACK_OFFENSIVE_BLOCKLIST` and inappropriate-content guard

### Changed
- Yoruba gold-meaning curation added
- Corpus fallback sampler hardened with length-ratio filtering and weighted-random selection

### Known Issues
- Parse-fallbacks still present (4 in v63)
- English too easy (91.7% consensus correct in v63)

---

## [v61] - 2026-06-20

### Added
- v61 N=1 Kaggle run: 36 MCQs from 3 proverbs
- Removed broken `adversarial-contrastive` prompt variant
- Prompt constraints updated to ±30% length parity

### Changed
- `LENGTH_CHECK_THRESHOLD` relaxed to 0.30 (±30%)
- Semantic-distance band widened (default max 0.85, Yoruba max 0.88)

### Known Issues
- Partial + fallback rate: 47.2%
- High-consensus-wrong rate: 25.0%
- Yoruba consensus correctness: 33.3%

---

## [v60] - 2026-06-20

### Added
- v60 N=1 Kaggle run: 45 MCQs from 3 proverbs
- Correct-meaning leak sanitizer (replaces leaking distractors instead of rejecting whole MCQ)
- Soft failure generator benching (threshold raised from 2 to 5)

### Changed
- `has_correct_meaning_leak()` converted from hard rejection to `_sanitize_correct_meaning_leak()`
- Fallback count and `leak_replaced` tracking added to `generate_options()`

### Known Issues
- `adversarial-contrastive` produced 0 generated items; 9/9 were length-fallback
- 28.9% partial + fallback

---

## [v59] - 2026-06-19

### Added
- P0 post-processing hardening: expanded idiom blocklist, correct-meaning leak detection, duplicate repair
- P1 NLI paraphrase filter (`cross-encoder/nli-deberta-v3-xsmall`)
- P2 evaluation additions: `compute_distractor_metrics()`, with-proverb baseline audit, human-annotation export
- 10 PNG visualizations

### Changed
- Duplicate detection converted to `repair_duplicate_options()` with near-duplicate repair
- Semantic-distance band relaxed (default max 0.82, Yoruba max 0.85)

### Known Issues
- 28.9% partial + fallback
- High-consensus-wrong rate: 22.2%
- Yoruba consensus correctness: 40.0%

---

## [v58] - 2026-06-20

### Added
- Initial v58 N=1 Kaggle run: 45 MCQs from 3 proverbs (1 English, 1 Arabic, 1 Yoruba)
- Baseline dynamic-generator + blind options-only audit pipeline
- Self-critique loop infrastructure
- Corpus fallback sampler
- Human-annotation export

### Known Issues
- Hard fallback rate: 0.0%
- Perfect consensus rate: 48.9% (target <30%)
- High-consensus-wrong rate: 22.2% (target <10%)
- Partial + fallback: 28.9% (target <15%)
- Yoruba consensus correctness: 40.0%
