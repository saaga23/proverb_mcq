# ProverbGap MCQ — Paper-First Pivot Outline

> **Trigger:** v69 fails or is marginal; project pivots to paper-first using v68/v69 outputs as production data.  
> **Last updated:** 2026-06-22  
> **Status:** Draft outline for internal planning and eventual EACL / ACL / EMNLP submission.

---

## 1. Proposed Title & Reframed Contribution

### 1.1 Proposed title

> **Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding**

**Alternative (more negative-results-forward):**

> *Why LLM-Generated Distractors Fail Cross-Lingually: A Failure Taxonomy from the ProverbGap Pipeline*

**Rationale.** The title foregrounds methodology and failure analysis rather than a clean benchmark release. If v69 remains marginal, the paper’s central contribution becomes: (a) a reproducible, hardened pipeline for adversarial distractor generation, (b) a documented failure taxonomy of LLM distractor generation across resource levels, and (c) the empirical observation that adversarial paraphrasing does not transfer difficulty to low-resource figurative language.

### 1.2 Reframed contribution

1. **Methodology.** A dynamic, multi-generator, cost-capped pipeline with disjoint blind-audit committee, dual-gate semantic validation (similarity + NLI + leakage + length), and deterministic fallback/repair logic.
2. **Failure taxonomy.** Six reproducible failure modes observed in v58–v69: same-family exploitation, chain-of-thought collapse, multi-stage-prompt triviality, position bias, API/provider fragility, and corpus-fallback quality collapse.
3. **Cross-lingual boundary.** English distractors degrade more under adversarial generation than Arabic/Yoruba, suggesting that paraphrase-based adversarial difficulty does not generalize to morphologically complex or low-resource settings.
4. **Dataset & artifacts.** A controlled, versioned set of v68/v69 MCQs with full raw outputs, cost logs, model IDs, and generation-status labels, released as a **testbed** rather than a final benchmark.

---

## 2. Abstract Structure

Target: **150–250 words** (EACL/ACL/EMNLP standard).

| Paragraph | Content |
|-----------|---------|
| **P1 — Motivation & gap** | LLM evaluation for figurative language is growing, but distractor generation remains under-validated, especially cross-lingually. Existing proverb benchmarks release MCQs without adversarial gates or blind audit. |
| **P2 — What we do** | We build a hardened adversarial distractor-generation pipeline for English, Arabic, and Yoruba proverb MCQs. The pipeline combines dynamic LLM generator pools, dual-gate semantic filtering, and a heterogeneous blind-audit committee that sees only the four options. |
| **P3 — Main finding** | Despite extensive hardening, distractor quality plateaus: partial+fallback rates remain high (v68/v69: ~XX–XX%), perfect consensus exceeds the 30% target, and high-consensus-wrong items persist. English remains trivially easy (≥90% consensus-correct), while Arabic and Yoruba suffer from low-quality corpus fallbacks and culturally mismatched distractors. |
| **P4 — Taxonomy & boundary** | We document a reproducible failure taxonomy linking each failure mode to a pipeline component. A cross-lingual boundary emerges: adversarial paraphrasing lowers English difficulty by X pp but barely affects Arabic/Yoruba, implying that surface-level paraphrase attacks fail to create hard negatives in low-resource figurative settings. |
| **P5 — Artifacts & framing** | We release the v68/v69 pipeline, audit logs, and N=XX MCQs not as a final benchmark, but as a public testbed for hardened distractor generation and failure-mode research. |

> **Placeholder rule:** all `XX%` values are to be filled from v68/v69 summary JSONs before submission. If v69 is marginal, use v68 as the primary production run and v69 as a sensitivity check.

---

## 3. Section Outline

### 3.1 Introduction (1.5 pages)
- Figurative-language evaluation gap; proverb understanding as a controlled test case.
- Why distractor quality matters: MCQ difficulty is determined more by distractors than by the stem.
- Current proverb benchmarks (ProverbEval, Jawaher, PRONE) release tasks without adversarial distractor validation.
- **Reframed contribution statement:** this paper studies *how to build and audit* adversarial proverb distractors, and reports the systematic failures that survive state-of-the-art hardening.
- Scope delimitation: MCQ-only, English/Arabic/Yoruba, OpenRouter API pipeline.

### 3.2 Related Work (1.5–2 pages)
- **Proverb/figurative-language benchmarks:** ProverbEval (MCQ+FiB+Generation, 6 languages), Jawaher, PRONE, PAWS-X, XLM-G.
- **Distractor generation:** DiVERT (distractor diversity), GSM-DC (math distractors), D-GEN, QG-generated foils, paraphrase-based negatives.
- **LLM-as-a-Judge / audit committees:** influence functions, model-as-a-judge bias, disjoint-pool contamination control.
- **Shortcut learning in MCQ:** position bias, length bias, lexical overlap, same-family exploitation.
- **Low-resource NLP evaluation:** cross-lingual transfer limits, data scarcity, morphological complexity.

### 3.3 Methodology: The Hardened Pipeline (3 pages)
- **Overview figure:** proverb + correct meaning → generator pool → prompt variants → dual-gate validation → option repair → blind audit committee → consensus label.
- **Generator pool:** dynamic substitution, preflight health checks, cost cap, resume state.
- **Prompt variants:** adversarial-length-locked, adversarial-hard-negative, plus retired variants as ablations.
- **Dual-gate validation:**
  - Gate 1: semantic distance band + NLI paraphrase filter + correct-meaning leak sanitizer.
  - Gate 2: length parity (±35%/±45%), idiom blocklist, duplicate repair, offensive fallback guard.
- **Fallback sampler:** corpus-based negative sampling; why it became the bottleneck in v66/v67.
- **Blind audit committee:** heterogeneous models, options-only input, rotating answer positions, consensus rules.
- **Reproducibility:** fixed seeds, versioned model IDs, raw output logs, cost tracker.

### 3.4 Datasets (0.75 page)
- English: 700 sampled from 2,278 proverbs (or v68/v69 actual N).
- Arabic: 913 complete corpus items.
- Yoruba: 700 sampled from 3,931 items.
- QA flags; FIX/DROP exclusion; gold-meaning curation (v64+) for all languages.
- Data provenance statement (CC BY 4.0 Arabic; Yoruba permission pending).

### 3.5 Experiments (1.5 pages)
- **Pilot progression:** v58 → v69, N=1 → N=5 → N=15.
- **Ablations:**
  - Single-generator vs. dynamic pool.
  - Disjoint vs. overlapping audit pools.
  - With/without length check, NLI filter, idiom blocklist.
  - S1 negative-sampling baseline vs. S2 adversarial generation.
- **Metrics:** hard-fallback rate, partial+fallback rate, perfect-consensus rate, high-consensus-wrong (HCW) rate, consensus accuracy, per-language correctness, duplicate rate, correct-key balance, cost.
- **Statistical tests:** bootstrap 95% CIs, McNemar for paired variant comparisons, binomial test for position bias.

### 3.6 Results (2.5 pages)
- **Main table (Table 3):** v68/v69 summary metrics across languages and overall.
- **Per-language consensus correctness:** English ≥90% (too easy), Arabic ~50%, Yoruba ~40–50%.
- **Partial+fallback and HCW rates by variant and language.**
- **Cost table:** generation + audit spend per run.
- **Position-bias analysis:** p < 0.0001 in earlier runs; report v68/v69 update.
- **Generator pool stability:** active/benched models, substitution counts.

### 3.7 Failure Taxonomy (2 pages)
Document the six failure modes observed across v58–v69. Each mode gets a subsubsection with: definition, pipeline locus, empirical magnitude, implication.

| # | Failure mode | Locus | Approx. magnitude (prior runs) |
|---|--------------|-------|--------------------------------|
| 1 | **Same-family exploitation** | Audit / evaluator | +31.1 pp accuracy when generator and auditor share lineage |
| 2 | **Chain-of-thought collapse** | Auditor prompting | 82.7% → 48% accuracy |
| 3 | **Multi-stage-prompt triviality** | Generator prompting | 100% accuracy, 0% fallback |
| 4 | **Position bias** | MCQ assembly | p < 0.0001; A-position 85.6% accuracy |
| 5 | **API/provider fragility** | Infrastructure | 90%+ failure rates, provider cascades |
| 6 | **Corpus fallback quality collapse** | Post-processing / fallback sampler | High HCW, partial+fallback > target |

Add v68/v69 rows for #6 if corpus fallback remains the dominant failure mode.

### 3.8 Human Validation Plan (1 page)
- **Why needed:** blind audit is a shortcut screen, not a validity certificate.
- **Sample:** 60 MCQs (20 per language), stratified by generation status, variant, and consensus level.
- **Annotators:** 2–3 native speakers per language (Upwork/Fiverr/university contacts).
- **Tasks:**
  1. Is the correct meaning accurate? (QA flag)
  2. Is each distractor plausible but wrong? (1–5 Likert)
  3. Is there an obvious shortcut (length, position, lexical overlap, generic idiom)?
- **Agreement:** Cohen’s κ ≥ 0.75 target; report exact value.
- **Gate:** <20% obvious-shortcut judgments required to support validity claims.
- **Budget:** ~$150–$300; contingency plan if budget is unavailable (report as limitation + planned validation).

### 3.9 Discussion (1.5 pages)
- **What the failure taxonomy means:** LLM-generated distractors for figurative language are brittle not because prompts are wrong, but because the fallback/repair layer cannot reliably recover from semantic-filter rejections without introducing confident wrong options.
- **Cross-lingual boundary interpretation:** English has denser paraphrase spaces; low-resource languages resist adversarial paraphrasing because model-generated paraphrases are often literal, awkward, or culturally mismatched.
- **Limitations:** MCQ-only scope, modest N, API reproducibility, no human validation yet, corpus fallback bottleneck, Yoruba source permission.
- **Ethics / bias:** potential for culturally inappropriate distractors; idiom/offensive blocklists; native-speaker review.

### 3.10 Conclusion (0.5 page)
- Summarize: hardened distractor generation is necessary but not sufficient for cross-lingual proverb MCQs.
- Call to action: future work should integrate human-in-the-loop curation, LLM-based fallback generation, and expanded language coverage.
- Reiterate artifact release as a testbed.

---

## 4. Key Figures and Tables

### 4.1 Figures

| # | Figure | Caption |
|---|--------|---------|
| 1 | Pipeline diagram | The hardened ProverbGap distractor-generation pipeline: dynamic generator pool → prompt variants → dual-gate validation → option repair → blind audit committee. |
| 2 | Per-language consensus correctness | Grouped bar chart of consensus accuracy by language for v68/v69; dashed line = random (25%). |
| 3 | Failure-mode summary | Horizontal bar chart of the six failure modes with approximate effect sizes from v58–v69. |
| 4 | Position-bias violin plot | Distribution of auditor accuracy by correct-key position (A/B/C/D) for v68/v69. |
| 5 | S1 vs. S2 / adversarial delta | S1 baseline vs. S2 adversarial consensus accuracy, with per-language deltas and 95% CIs. |
| 6 | Generator pool dynamics | Active/benched models and substitution counts across the run. |
| 7 | Cost vs. quality frontier | Total cost (USD) vs. partial+fallback rate and HCW rate across v58–v69. |
| 8 | Human validation preview | If available: annotator plausibility scores and shortcut-flag rates by language. |

### 4.2 Tables

| # | Table | Content |
|---|-------|---------|
| 1 | Comparison with existing benchmarks | Task types, languages, human validation, distractor methodology, size. |
| 2 | Prompt variants and gate thresholds | Per-variant constraints and validation thresholds. |
| 3 | v68/v69 dataset statistics | N per language, generation status distribution, cost. |
| 4 | Audit committee composition | Model IDs, family, role, substitution rationale. |
| 5 | Failure-mode taxonomy | Phenomenon, pipeline locus, magnitude, implication, mitigation. |
| 6 | Per-language distractor quality metrics | Perplexity, embedding diversity, fallback rate, HCW rate. |
| 7 | Ablations | Single vs. pool, disjoint vs. overlapping, with/without length/NLI checks. |
| 8 | Human validation results | Agreement (κ), plausibility means, shortcut-flag proportions. |

---

## 5. Reviewer-Risk Mitigation

### 5.1 Low N / modest sample size

**Risk:** Reviewers reject claims because v68/v69 may cover only 15–45 proverbs per language.

**Mitigation:**
- Frame the paper as a **methodology + failure-taxonomy** contribution, not a benchmark-scale claim.
- Report all Ns and CIs explicitly; avoid over-generalizing to entire languages.
- Use the modest N as a deliberate choice: the paper shows what breaks *even at small scale*, which is methodologically informative.
- Propose a larger N=50/language follow-up as future work, with budget estimate.
- Include power analysis: with 15 proverbs/language and 4 MCQs each, detect a 15 pp difference in consensus accuracy at α=0.05, power≈0.60; with 45 proverbs, power≈0.85.

### 5.2 High high-consensus-wrong (HCW) rate

**Risk:** High HCW is read as “the distractors are confidently wrong,” undermining validity.

**Mitigation:**
- Make HCW a **primary object of study**, not a hidden weakness. Name it as the central failure mode.
- Trace HCW to its sources: NLI false positives → corpus fallback; generic-English idiom leaks; near-paraphrase distractors.
- Show that HCW is concentrated in specific variants/languages, not random noise.
- Include human validation that explicitly asks: “Did any distractor look more correct than the key?” This validates whether HCW maps to human perception.
- Add a “quality-repair” ablation: if HCW drops when LLM-based fallback generator is enabled (if tested in v69), report it.

### 5.3 Corpus fallback bottleneck

**Risk:** Corpus-sampled fallbacks are seen as a design flaw that invalidates the distractors.

**Mitigation:**
- Acknowledge the bottleneck in the abstract and discussion.
- Quantify: report fallback_count distribution, per-language fallback sources, and HCW rate among fallback items.
- Explain the design rationale: corpus fallbacks were intended as a deterministic, reproducible safety net under cost constraints.
- Position the corpus fallback as a **baseline condition** and propose an LLM-based fallback generator as the next experiment.
- Include an ablation table comparing MCQs with/without fallback replacements.

### 5.4 No human validation yet

**Risk:** Reviewers require human validation for any MCQ validity claim.

**Mitigation:**
- Do not claim the MCQs are valid for human test-takers. Claim only that the **pipeline and audit methodology** are reproducible and that the failure taxonomy is empirically grounded.
- Include a concrete Human Validation Plan section with sample size, annotator recruitment, tasks, agreement metric, budget, and timeline.
- Add a limitations paragraph: “Human validation is pending; the blind audit is a necessary but insufficient shortcut screen.”
- If submission deadline permits, run the 60-item human validation *before* submission and move results to Section 5.8/Table 8.
- If not, state the study is registered/underway and include a pre-registration note.

---

## 6. Target Venues and Timeline

### 6.1 Target venues

| Venue | Deadline | Fit | Strategy |
|-------|----------|-----|----------|
| **EACL 2027 (ARR)** | August 3, 2026 | Best fit: methodology-first, low-resource focus, European venue. | Primary target. |
| **ACL 2027 (ARR)** | October 2026 (est.) | Strong fit if human validation is completed. | Secondary target if EACL misses or if validation data strengthens the paper. |
| **EMNLP 2026 direct** | July 2026 (est., passed/approaching) | Tight timeline; use only if v69 is clean and human validation can be done in <4 weeks. | Emergency target; likely too late. |
| **Fig-Lang / MRL / LR4NLP workshop** | Co-located with EMNLP/ACL | Good fallback if main-conference reviews flag scope/sample size. | Workshop plan if desk-rejected. |

### 6.2 Timeline (paper-first pivot)

| Week | Dates | Milestone |
|------|-------|-----------|
| W0 | June 22–28, 2026 | Finalize v68/v69 run analysis; fill all `XX%` placeholders; decide if v69 is primary or sensitivity run. |
| W1 | June 29–July 5 | Draft Related Work + Methodology sections; produce Figures 1–3 and Tables 1–4. |
| W2 | July 6–12 | Draft Results + Failure Taxonomy; produce Figures 4–7 and Tables 5–6. |
| W3 | July 13–19 | Run human validation subset (if budget/time allows); draft Human Validation section. |
| W4 | July 20–26 | Full paper draft; internal review; reviewer-risk mitigation checklist. |
| W5 | July 27–Aug 2 | Polish, compile reproducibility package, submit to EACL ARR. |

### 6.3 Contingencies

- **If v69 is only marginal:** Use v68 as primary production run; v69 as robustness check.
- **If human validation cannot be completed by August 3:** Keep Human Validation Plan as a section, label study as in-progress, and submit to EACL ARR with the plan as a commitment.
- **If EACL ARR rejects on scope/sample size:** Reframe for ACL 2027 with completed human validation and expanded N=50/language generation.

---

## 7. Living Document

This outline should be updated after v68/v69 analysis is complete. Fill the placeholders above and adjust the failure taxonomy and figures as the data dictate.

**Next update trigger:** v69 summary JSON + audit CSVs are available.
