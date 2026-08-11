# Elite Research Execution Plan — ProverbGap MCQ (Pilot 1 TEST)

**Framework:** Elite Research Execution Framework (EMNLP / ACL / NeurIPS standard)  
**Project:** ProverbGap MCQ distractor-generation and blind-audit pipeline  
**Current artifact:** `openrouter_pilot_distractor_generation_test_nano_opus.ipynb`  
**Date:** 2026-06-16  
**Status:** Pilot / method-validation phase

---

## 1. Research question and intended claims

### Primary question
Can a **diverse, dynamic pool of LLM generators** plus an **independent blind-audit committee** produce proverb MCQ distractors that are:

1. **Semantically plausible** (look like real meanings),
2. **Shortcut-resistant** (not solvable from surface cues alone), and
3. **Cross-lingually stable** (English, Arabic, Yoruba)?

### Claims we might eventually submit (each needs independent evidence)

| Claim | Evidence required | Current status |
|-------|-------------------|----------------|
| A multi-model generator pool is more robust than a single model. | Compare fallback/parse-failure rates across solo vs. pooled generation; report substitutions. | Being tested in Pilot 1 TEST. |
| A disjoint blind-audit committee detects surface shortcuts. | Consensus accuracy on generated MCQs; failure rate without proverb/meaning. | Methodology in place; needs human calibration. |
| Prompt variants differ in shortcut tendency. | Per-variant consensus accuracy and per-model disagreement. | Pilot will produce this. |
| The distractors are valid for human test-takers. | Human validation subset with inter-annotator agreement (Cohen's κ ≥ 0.75). | **Not yet done.** Blocker for any submission claim. |
| The pipeline is reproducible and cost-controlled. | Pinned environment, versioned model IDs, raw outputs, cost history, replication checklist. | Partially in place. |

### Falsification criteria

- If >25% of generation calls result in `hard_fallback` after preflight substitution, the generator pool is **not** robust enough.
- If blind-audit consensus accuracy is >45% (FAIL threshold) for most generator/variant combinations, the distractors leak surface cues.
- If human validators cannot agree that the generated distractors are plausible (κ < 0.6), the MCQs are not valid.
- If the same model appears in both generation and audit pools and results shift when it is excluded, audit contamination exists.

---

## 2. Phase plan

### Phase 0 — Methodological lock (current)

- [x] Define generator and audit pools.
- [x] Enforce disjointness between generator and audit pools.
- [x] Implement dynamic substitution on failure.
- [x] Implement cost cap, resume state, raw-output logging.
- [x] Add parser self-test and output validation.
- [ ] **TODO:** Pin `requirements.txt` and environment snapshot.
- [ ] **TODO:** Add deterministic seed documentation (already `SEED = 20260615`).

### Phase 1 — Pilot 1 TEST (N=3 per language)

**Goal:** Validate the response-capture and substitution mechanics, not to produce publishable results.

- [ ] Upload notebook to Kaggle.
- [ ] Run full pipeline with `N_PER_LANG = 3`.
- [ ] Inspect:
  - `raw_outputs.csv` for empty content.
  - `generated_mcqs.csv` for `generation_status` distribution.
  - `audit_results.csv` for missing votes.
  - `summary.json` for cost and substitutions.
- [ ] Decision gate: proceed to Phase 2 only if:
  - Hard-fallback rate < 10%,
  - Active pool remains ≥ 3 generators and ≥ 3 auditors,
  - Audit consensus accuracy is interpretable (not random, not trivially high).

### Phase 2 — Medium-scale validation (N=10 per language)

**Goal:** Collect enough data for per-variant comparison and preliminary shortcut analysis.

- [ ] Increase `N_PER_LANG = 10` (30 proverbs × 6 generators × 5 variants = 900 generation calls).
- [ ] Re-run with same seeds and pool state from Phase 1 if healthy.
- [ ] Add per-language, per-variant, per-generator summary tables.
- [ ] Run position-bias check (shuffled answer positions).
- [ ] Run length-bias ablation (compare vs. length-matched corpus distractors).

### Phase 3 — Human validation subset

**Goal:** Anchor the blind-audit signal to human judgments.

- [ ] Sample 50 MCQs across languages and variants.
- [ ] Recruit 2 native speakers per language (Upwork / Fiverr / university contacts).
- [ ] Tasks: (a) is the correct meaning accurate? (b) are distractors plausible but wrong? (c) is there an obvious shortcut?
- [ ] Compute Cohen's κ and report proportion of “obvious shortcut” judgments.
- [ ] Gate: κ ≥ 0.75 and <20% obvious-shortcut judgments.

### Phase 4 — Full-scale generation + baselines

**Goal:** Produce the final dataset and comparison table for the paper.

- [ ] Generate S1 (negative sampling) baseline with strict filters.
- [ ] Generate S2-style adversarial distractors from the best generator/variant combinations identified in Phase 2.
- [ ] Include strong baselines: mBERT, XLM-R, AraBERT, AfriBERTa sentence-similarity selector.
- [ ] Include recent LLM baselines (GPT-4.1, Qwen3, Llama-4).
- [ ] Run full blind audit on all generated MCQs.
- [ ] Report cost, carbon, and compute budget.

### Phase 5 — Paper / submission package

- [ ] Reproducibility checklist (code, data, seeds, configs, model IDs, costs).
- [ ] Reviewer-response pre-document addressing all simulated critiques below.
- [ ] Limitations section explicitly discussing construct validity, human validation gap, and API reproducibility.
- [ ] Target venue selection based on novelty scope.

---

## 3. Risks and failure modes (identified before compute spend)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenRouter model IDs change or models are removed. | Medium | High | Live catalog filter + pool substitution + versioned model list in summary. |
| GPT-5 or other reasoning auditors return empty content. | Medium | High | Use `max_completion_tokens`; bench on empty; substitute. |
| Generator pool collapses below minimum during preflight. | Low-Medium | High | Reserve pool of substitutes; abort with saved state. |
| Distractors leak source-language words. | Medium | High | Existing filter for source-text leakage; add explicit lexical-overlap check. |
| Correct meaning is systematically longer/shorter than distractors. | Medium | High | Length check (±35%); add length-matched ablation. |
| Position bias makes correct answer predictable. | High | Medium | Deterministic rotating position; report position-bias analysis. |
| Same-family generator/auditor share failure modes. | Low | Medium | Disjoint pools; report per-family breakdown. |
| Cost cap exceeded mid-run. | Low | Medium | `would_exceed()` on every call; periodic saves. |
| Human validation too expensive or slow. | Medium | High | Start with 50-item subset; expand if κ is promising. |

---

## 4. Assumptions and how to falsify them

| Assumption | Why it matters | Falsification test |
|------------|----------------|--------------------|
| Blind audit consensus approximates shortcut risk. | Core validity claim. | Compare consensus accuracy against human “obvious shortcut” judgments on a subset. |
| Multi-model pool improves robustness. | Main methodological contribution. | Compare parse/fallback rates between single-generator and pooled runs. |
| Generated distractors are semantically distinct from the correct meaning. | Distractor validity. | Human validators rate plausibility; also check paraphrase overlap with BERTScore. |
| 3 proverbs per language is enough for Pilot 1. | Scope claim. | It is only for pipeline validation, not for conclusions. Never extrapolate Pilot 1 to language-level trends. |
| OpenRouter pass-through pricing is stable. | Cost claims. | Refresh price table from `/models` and report timestamp. |
| `TEMPERATURE = 0.0` gives deterministic outputs. | Reproducibility. | Run duplicate calls on a small subset and measure exact-match rate. |

---

## 5. Reviewer simulation

### Methodology critique

> "Why should a blind options-only audit be considered sufficient for distractor quality?"

**Response:** It is not sufficient. It is a necessary shortcut screen. Human validation is required for validity claims. We will explicitly state this limitation and report a human subset.

> "Why are generators and auditors disjoint? Couldn't a substitute later reintroduce overlap?"

**Response:** The starter pools are disjoint, and substitutes are chosen from outside the opposing pool. We log all substitutions and can verify post-hoc that no active generator was also an active auditor for the same MCQ batch.

> "Why 30%/45% thresholds for PASS/REVIEW/FAIL?"

**Response:** They are heuristics calibrated to signal “well above random” (25%) but below “clear shortcut.” We will report the raw distribution and justify thresholds with human calibration data.

### Dataset critique

> "Your dataset mixes Yoruba (low-resource), Arabic (morphologically complex), and English. Isn't this confounded by resource availability?"

**Response:** We report per-language results separately and do not pool languages for the main claim. Cross-lingual stability is a secondary claim requiring per-language human validation.

> "The Arabic gold standards have known errors. How do you handle that?"

**Response:** We have a QA flag column and will exclude FIX/DROP items; we will also spot-check a sample and report estimated gold-error rate.

### Evaluation critique

> "You use only consensus accuracy. Where are significance tests, confidence intervals, and calibration?"

**Response:** For Pilot 1 we focus on diagnostic rates. At scale we will bootstrap CIs, report per-model CIs, and include calibration measures (e.g., ECE on audit confidence if available).

### Reproducibility critique

> "OpenRouter models may change. How can I reproduce this in six months?"

**Response:** We version all model IDs, snapshot the live catalog, log raw responses, provide seeds, and include a fallback deterministic S1 baseline that uses only local corpus sampling.

### Fairness / bias critique

> "Could the distractors encode cultural or regional bias?"

**Response:** We sample across languages and will report per-language performance. Human validators are native speakers who can flag culturally inappropriate distractors.

### Novelty critique

> "Dynamic model pools for MCQ generation are not novel."

**Response:** The novelty is not the pool mechanism per se, but its application to adversarial proverb distractor generation with explicit disjoint-audit contamination control and low-resource cross-lingual validation. We will compare against single-model and naive S2 baselines.

### Practicality critique

> "This relies on expensive API calls. Is it realistic?"

**Response:** Pilot 1 costs ~$1. Full generation is more expensive, but we report costs and provide a cheaper local baseline. The final dataset is a one-time creation cost.

---

## 6. Dataset standards compliance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Multiple datasets | Partial | English, Arabic, Yoruba proverbs; all from the ProverbGap corpus. |
| Diverse domains | N/A | Proverbs are a single genre by design. |
| Origin documented | Partial | `actual_data/data_inventory.txt` exists; Yoruba source is a copyrighted book requiring permission. |
| License documented | Partial | Arabic CC BY 4.0; Yoruba derived from copyrighted material; English scraped. |
| Annotation process | Partial | Existing QA flags; need human validation subset. |
| Harmonization | In progress | Column renaming handled in `load_data()`; duplicates and QA flags need filtering. |

**Action:** Fill `DATA_PROVENANCE_TEMPLATE.md` before submission. Obtain Yoruba book permission or scope claim to Arabic/English if unavailable.

---

## 7. Evaluation standards compliance

| Evidence category | Planned | Status |
|-------------------|---------|--------|
| Main metric (blind audit consensus accuracy) | Yes | In place. |
| Statistical significance (bootstrap CIs) | Yes | Add at Phase 2. |
| Calibration measure | Maybe | Audit does not produce confidence; VCE not applicable here. |
| Robustness (position/length/family ablations) | Yes | Add at Phase 2. |
| Error analysis | Yes | Inspect high-consensus items for leakage/length bias. |
| Human evaluation | Yes | Phase 3. |
| Generalization (cross-language) | Yes | Per-language reporting. |
| Cost analysis | Yes | Cost tracker logs every call. |
| Fairness analysis | Partial | Per-language; no demographic breakdown available. |

---

## 8. Baseline standards compliance

| Baseline type | Candidate | Status |
|---------------|-----------|--------|
| Classical / encoder | mBERT, XLM-R, AraBERT, AfriBERTa cosine-similarity selector | Existing in project; needs integration. |
| Strong established LLM | GPT-4.1, Qwen3, Llama-4 as generators | In generator pool. |
| Naive strategy | S1 negative sampling | Existing. |
| Flawed strategy | S2 paraphrase distractors | Existing; will report as negative result. |
| Ablations | Single-generator vs. pool; disjoint vs. overlapping audit; with/without length check | Plan at Phase 2. |

---

## 9. Statistical standards compliance

- [x] Random seed fixed (`SEED = 20260615`).
- [ ] Bootstrap confidence intervals for consensus accuracy.
- [ ] Variance across answer-position shuffling.
- [ ] Report sample sizes and missing-data rates.
- [ ] Use paired tests when comparing variants on the same proverbs.

---

## 10. Error analysis standards

Planned investigations:

1. **High-consensus failures:** Items where auditors agree on the correct answer despite no proverb/meaning. Inspect for length, lexical, or structural leakage.
2. **Low-consensus items:** Items where auditors disagree. May indicate noisy or ambiguous proverbs; useful for dataset cleaning.
3. **Per-language failure modes:** Arabic morphology, Yoruba orthography, English colloquialism.
4. **Per-generator failure modes:** Which generators produce the most shortcuts? Which produce the most unparseable outputs?

---

## 11. Novelty mapping

| What exists | What is new here |
|-------------|------------------|
| LLM-generated MCQ distractors (general) | Application to **proverb understanding** in low-resource languages. |
| Single-model distractor generation | **Dynamic, failure-driven multi-model pool** with automatic substitution. |
| Blind audit for shortcut detection | **Disjoint generator/audit pools** to prevent contamination. |
| S2 paraphrase distractors | Using the failure of S2 as a **motivated baseline** and combining pool generation with audit screening. |

Risk: The pool mechanism itself may be considered engineering, not science. Mitigation: Frame the contribution as a **methodology for robust, auditable distractor generation under API uncertainty**, validated on a hard low-resource task.

---

## 12. Improvement protocol (for any future change)

Before implementing a new prompt, model, filter, or metric:

1. **Hypothesis:** State what it should improve and why.
2. **Expected benefit:** Quantified target (e.g., reduce hard fallback by 5pp).
3. **Failure risks:** What could go wrong (e.g., new model too expensive, prompt leaks answers).
4. **Computational cost:** Estimated API spend and runtime.
5. **Evaluation plan:** Which metric and which subset will decide success.
6. **Success criteria:** Threshold for adopting the change.
7. **Rollback criteria:** Threshold for reverting.

**Example:** Adding a new generator.
- Hypothesis: Llama-4-Maverick produces more diverse distractors than Qwen.
- Benefit: Lower within-family correlation.
- Risk: It may fail preflight due to output format.
- Cost: ~$0.05 for Pilot 1.
- Plan: Add to pool, run Pilot 1, compare parse-failure rate and audit consensus.
- Success: hard-fallback rate ≤ 10% and consensus within target band.
- Rollback: bench if hard-fallback rate > 25%.

---

## 13. Immediate next actions

1. **Upload and run** `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` on Kaggle with `N_PER_LANG = 3`.
2. **Inspect outputs** against the decision gate in Phase 1.
3. **Create `requirements.txt`** with pinned versions (`requests`, `pandas`, `numpy`, `python-dateutil`, `pytz`).
4. **Fill `DATA_PROVENANCE_TEMPLATE.md`** for all three languages.
5. **Plan human validation budget** (~$150–$300 for 50 items × 2 annotators × 3 languages).
6. **Do not** scale to Phase 2 until Phase 1 gate is passed.

---

## 14. Living document

This plan should be updated after every major run. Record:

- Date of run.
- Active/benched models.
- Fallback rates.
- Audit consensus distribution.
- Cost.
- New reviewer criticisms that emerged.
- Decisions made and why.
