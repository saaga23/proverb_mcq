# ProverbGap MCQ — Deep Gap / Liability Analysis
**Date:** 2026-07-10  
**Scope:** v68 production dataset (180 MCQs) + paper-first artifacts + legacy pipeline claims  
**Venue risk:** EACL 2027 ARR (submission 3 Aug 2026)

---

## Executive Summary

The project has strong engineering rigor (dynamic pools, blind audit, adversarial prompts, gold-meaning curation) but the **paper-first artifacts contain fatal inconsistencies between claims and evidence**. The abstract and `table7_failure_taxonomy.csv` cite legacy Groq-pipeline numbers (2,313 MCQs, S1 86.8% vs S2 62.5%, encoder baselines, 31.1pp same-family exploitation) that are **not present in the current v68 production dataset**. Reviewers will desk-reject or major-reject on these authenticity/reproducibility grounds alone.

Secondary risks cluster around: (a) small dataset size (180 MCQs) with no statistical significance tests, (b) severe audit-committee position bias (A-position 73.3% vs D-position 46.7%), (c) unfilled data-provenance documentation with a known Yoruba copyright issue, (d) missing baselines in current outputs, and (e) the corpus-fallback bottleneck remaining unfixed due to budget exhaustion.

---

## 1. Dataset Size Adequacy

### P0 — Abstract claims 2,313 MCQs; production dataset is 180
| Source | Claimed size | Actual available |
|--------|-------------|------------------|
| `docs/ProverbGap_Reframed_Title_Abstract.md` | "2,313 MCQs (English 700, Arabic 913, Yoruba 700)" | **180 MCQs** (v68, N=5) |
| Legacy Pilot 2 Groq pipeline | 900+ MCQs | Archived, not part of current methodology |
| Current OpenRouter Pilot 1 TEST | 180 MCQs | Validated, full audit |

**Risk:** Reviewers will check the released dataset or ask for the count in the experiments section. A 13× gap between abstract claim and released data is an automatic desk-reject or major-reject trigger at ACL/EACL.

**Fix:**
1. **Immediately** rewrite the abstract to state **180 MCQs** (or the final N=15 count if v70 runs).
2. Remove or explicitly footnote the legacy 2,313 number as "prior pilot scale."
3. Do not release or cite the legacy Groq S1/S2 CSVs as part of the current methodology unless they are re-audited with the hardened pipeline.

### P1 — 180 MCQs is small for a cross-lingual benchmark claim
Even framed as a methodology paper, 180 MCQs (60 per language) is thin for per-language statistical claims. The 60-item human-validation sample is below the 90-item recommendation in `annotation/sample_size_analysis.py`.

**Fix:**
1. Run v70 at N=15 (45 proverbs → 540 MCQs) as soon as budget renews.
2. If N=15 is blocked, explicitly frame the paper as a **methodology + failure-taxonomy study with N=5** and avoid strong per-language generalization claims.
3. Increase human-validation sample to **90 items (30 per language)** to match the sample-size analysis recommendation, or justify 60 with a power analysis.

### P2 — Stratification depth
The 60-item validation sample stratifies by `generation_status` (25 generated, 19 partial, 16 length_fallback) but not by variant or generator. Reviewers may ask whether the sample represents the full generator×variant space.

**Fix:** Stratify the human-validation sample by both language and variant (at minimum 5 items per cell).

---

## 2. Evaluation Methodology Gaps

### P0 — Missing encoder baselines in current outputs
The abstract claims: `"encoder baselines (mBERT 54.7%, XLM-R 55.3%, AraBERT 54.0%, AfriBERTa 56.7%)"`. These numbers **do not appear in any v68 paper-first output table**.

**Risk:** Reviewers will ask to reproduce these numbers or compare against them. If they are from a different pipeline, this is data fabrication or, at best, misleading citation.

**Fix:**
1. **Either** re-run the encoder baselines on the v68 dataset and add the results to `table4_per_generator_metrics.csv` or a new `table_encoder_baselines.csv`.
2. **Or** remove the encoder baseline claim from the abstract and paper until they are re-executed.

### P0 — Missing S1 vs S2 comparison in current methodology
The abstract cites `"Strategy 1: 86.8%; Strategy 2: 62.5%; McNemar p < 0.001"` and `"English accuracy drops 8.9pp under S2, whereas Arabic and Yoruba drop only 2.2pp"`. These are from the **legacy Groq Pilot 2 S1/S2 pipeline (N=10)**, not from the current OpenRouter distractor-generation pipeline.

**Risk:** The current v68 pipeline does not have an S1/S2 split in this form. The 4 variants (`adversarial-hard-negative`, `adversarial-length-locked`, `overgenerate-select`, `taxonomy-guided`) are prompt variants, not strategies. Mixing legacy S1/S2 numbers with the new methodology invalidates the cross-lingual boundary claim.

**Fix:**
1. **Do not mix** legacy Pilot 2 S1/S2 numbers with Pilot 1 TEST v68 numbers in the same paper without explicit separation and re-validation.
2. If the S1/S2 comparison is central, re-run it on the hardened OpenRouter pipeline with the disjoint audit committee.
3. If the distractor-generation failure taxonomy is central (recommended), reframe the paper entirely around v68 and drop the S1/S2 language.

### P1 — No length-bias, position-shuffling, or distractor-efficiency metrics
The Elite Research Execution Plan lists these as required for Phase 2/4, but the paper-first outputs do not contain:
- Length-bias ablation (does longer = more plausible?)
- Option-shuffling robustness (flip rate)
- Distractor-efficiency metrics (functional vs. non-functional)
- All-A / all-D / random baselines

**Fix:**
1. Add a `table_length_bias.csv` correlating option length with auditor selection.
2. Add a `table_shuffling_robustness.csv` from re-shuffling a 20-item subset.
3. Add heuristic baselines (all-A, all-D, random) to `table1_aggregate_metrics.csv`.

### P1 — Blind options-only audit is supplementary, not primary
The literature review (`agent_literature_shortcut_audit.md`) correctly concludes the audit is a "necessary shortcut screen" but not sufficient. However, the paper-first outputs treat consensus accuracy as the headline metric without a human-calibration anchor.

**Fix:**
1. Explicitly state in the paper that consensus accuracy is a **proxy for shortcut resistance**, validated against human plausibility ratings.
2. Report the LLM-proxy IAA (Fleiss κ=0.67) as a ceiling estimate, but do not claim it substitutes for human annotation.

---

## 3. Statistical Rigor Gaps

### P0 — No significance tests in paper-first outputs
The legacy runs used McNemar (χ² = 131.3, p < 0.001) and bootstrap CIs. The v68 paper-first outputs contain **bootstrap CIs** for consensus accuracy but **no paired tests, no McNemar, no Wilcoxon, no ANOVA** for comparing variants, generators, or languages.

**Risk:** Reviewers will ask whether the per-variant and per-language differences are statistically significant. Without tests, the paper is descriptive, not inferential.

**Fix:**
1. Add McNemar’s test for paired comparisons (e.g., `adversarial-hard-negative` vs. `overgenerate-select` on the same 15 proverbs).
2. Add a non-parametric test (Wilcoxon signed-rank or Friedman) for per-generator and per-variant accuracy distributions.
3. Add multiple-comparison correction (Holmes-Bonferroni or FDR) for the 4-variant × 3-language post-hoc tests.

### P1 — CIs missing for secondary metrics
Bootstrap CIs are reported only for `consensus_accuracy`. Missing for:
- `perfect_consensus_rate`
- `hcw_rate`
- `partial_or_fallback_rate`
- `hard_fallback_rate`

**Fix:** Compute and report 95% bootstrap CIs for all six metrics in `table1_aggregate_metrics.csv` and `table2_per_language_metrics.csv`.

### P1 — No variance decomposition
The paper does not report variance across generators, variants, or shuffles. For example, `qwen/qwen3.7-max` has 30% length_fallback vs. `gemma-4-31b-it` at 10%, but there is no test of whether this difference is significant.

**Fix:** Add a variance-component table (e.g., random-effects logistic regression or ANOVA) partitioning variance into language, variant, generator, and proverb-level effects.

### P2 — Determinism not validated
The seed `SEED = 20260615` is fixed, but there is no reported exact-match rate for duplicate API calls at `temperature=0.0`. The fallback generator uses `temperature=0.0`, but the main generators use `temperature=0.7` (assumed from standard configs; not documented in paper outputs).

**Fix:**
1. Document the exact temperature per pool (generator vs. audit vs. fallback).
2. Report the duplicate-call exact-match rate as a reproducibility metric.

---

## 4. Reproducibility Gaps

### P0 — No environment pinning
`requirements.txt` uses `>=` without a lockfile. There is no `pyproject.toml`, no Dockerfile, and no conda environment file.

**Risk:** Reviewers or downstream users cannot reproduce the exact environment. Sentence-transformers, pandas, numpy, and requests versions can drift and change NLI/paraphrase-filter behavior.

**Fix:**
1. Generate `requirements.lock` (e.g., `pip freeze > requirements.lock`) from the exact Kaggle/local environment.
2. Add a `Dockerfile` or `environment.yml` with pinned versions.
3. Commit the exact `kaggle_runner_packages.txt` from the Kaggle notebook.

### P0 — Model versioning is textual, not machine-readable
Model IDs are recorded in `pilot1_test_summary.json`, but there is no snapshot of the OpenRouter `/models` catalog at run time. If a model is renamed, deprecated, or re-weighted, reproduction fails.

**Fix:**
1. Save the full `/models` JSON response (or at least the subset used) to `openrouter_catalog_snapshot_<timestamp>.json` at the start of every run.
2. Record the exact `pricing` fields (prompt/completion tokens) used for cost calculation.

### P1 — Cost transparency is aggregate
The paper reports total cost ($0.85) but no per-item, per-model, or per-phase breakdown.

**Fix:**
1. Add `cost_by_model.csv` and `cost_by_phase.csv` to the paper outputs.
2. Report cost per MCQ, per language, and per variant.

### P1 — No seed/resume audit
The code uses `SEED = 20260615`, but the paper-first outputs do not include a reproducibility checklist verifying that a fresh run reproduces the exact 180 MCQs.

**Fix:**
1. Add a `REPRODUCIBILITY_CHECKLIST.md` with hash checksums of all output CSVs.
2. Run a local end-to-end reproduction and record the hash match rate.

### P2 — Kaggle notebook drift risk
The Kaggle notebook is regenerated from `.py` source via `convert_test_nano_opus_to_notebook.py`, but there is no CI check ensuring they stay in sync.

**Fix:**
1. Add a pre-commit or CI check that diffs the notebook against freshly converted output.
2. Include a git hash of the source `.py` file inside the notebook metadata.

---

## 5. Data Provenance Gaps

### P0 — `DATA_PROVENANCE_TEMPLATE.md` is largely empty
The template has fields for Yoruba, English, and Arabic provenance, but most are blank. EACL reviewers require complete provenance documentation.

**Fix:**
1. Fill every blank in `DATA_PROVENANCE_TEMPLATE.md` before submission.
2. Attach it as an appendix.

### P0 — Yoruba copyright risk
The Yoruba data is derived from *Yoruba Proverbs* by Oyekan Owomoyela (University of Nebraska Press, 2005, ISBN 978-0-8032-1843-7). The book is **under copyright**. The data inventory notes "Personal copy / acquired PDF" but there is **no documented permission** for redistribution.

**Risk:** The publisher can demand removal of the dataset. EACL requires data licensing documentation.

**Fix:**
1. Contact University of Nebraska Press for permission to distribute the extracted proverbs, or
2. Scope the paper to **English and Arabic only** and release only those subsets, or
3. Release only the **MCQ artifacts** (not the raw proverb corpus) under a data-derivation argument, with explicit citation of the source book.

### P1 — English data sources undocumented
The English data is listed as "Multiple websites (scraped)" but no URLs, scraping dates, tools, or rights are documented.

**Fix:**
1. Document every scraped URL, date, and selection criterion.
2. Verify `robots.txt` compliance and fair-use status.
3. If sources are unclear, replace with a well-documented public-domain compilation (e.g., *Oxford Dictionary of Proverbs* if out of copyright).

### P1 — Arabic data provenance unclear
The Arabic dataset uses IDs like `MID0001`, but the template does not explain the `MID` prefix, the source dataset name, authors, or license.

**Fix:**
1. Identify the source dataset (HuggingFace ID, paper, or website).
2. Document the license and citation requirements.
3. Explain the 913-item subset selection criteria.

### P2 — Missing QA-flag filtering
The Yoruba inventory shows 3,834 rows with missing `QA_Flag` and 3,748 with missing `Comments`. The paper does not report how many proverbs were filtered out before sampling the 5-per-language set.

**Fix:**
1. Report the filtering pipeline: raw count → deduplicated → QA-pass → sampled.
2. Include a `data_subsampling_report.csv` in the outputs.

---

## 6. Methodology Weaknesses

### P0 — Corpus fallback sampler is the confirmed bottleneck
v68 confirmed: 43.9% partial+fallback, mean 0.99 replacements per MCQ, 27.8% HCW. The v69 LLM-fallback ablation was **blocked by OpenRouter budget exhaustion** (`403 Budget limit exceeded`). The core engineering problem remains unsolved.

**Risk:** The paper’s central methodological claim (hardened adversarial generation) is undermined by the fact that the fallback path — used in nearly half the items — produces confident-wrong distractors.

**Fix:**
1. **Renew the OpenRouter budget immediately** and run v69/v70.
2. If budget renewal is delayed, frame the corpus-fallback failure as the **primary negative result** and build the paper around the failure taxonomy rather than claiming success.
3. Add a `fallback_quality_ablation.csv` comparing corpus vs. LLM fallback on a 20-item pilot (if any LLM fallback runs exist).

### P1 — NLI and leak filters are over-aggressive
Mean replacements per MCQ: NLI 0.36, leak 0.35, length 0.15. The filters are removing tempting distractors and forcing fallback use. The current thresholds (`NLI_EMBEDDING_GUARD_BY_LANGUAGE`: Arabic/Yoruba 0.45, default 0.55) may be too low for Arabic/Yoruba and too high for English.

**Fix:**
1. Run a grid search over NLI embedding guards (0.40–0.65) and leak thresholds (0.75–0.90) on a held-out 20-item subset.
2. Report the threshold sensitivity as an ablation.

### P1 — Yoruba is fragile despite curation
Yoruba consensus correctness is 51.7% (barely above the 50% gate) with 33.3% HCW. Gold-meaning curation (`curate_gold_meaning()`) improved literal glosses but did not fix culturally mismatched corpus fallbacks.

**Fix:**
1. Add a Yoruba-specific corpus fallback that samples only from Yoruba proverbs (cross-lingual contamination is a known failure mode).
2. Add a cultural-expert review step for Yoruba distractors before inclusion.

### P1 — English is too easy
English consensus accuracy is 65.0% with 45.0% perfect consensus. Distractors are not tempting enough for English proverbs.

**Fix:**
1. Increase English NLI embedding guard to 0.60–0.62 to allow more subtle near-paraphrases.
2. Add an English-specific prompt variant that targets common misreadings of well-known proverbs.

---

## 7. Missing Baselines

### P0 — No baselines in current v68 outputs
The abstract claims encoder baselines, but `paper_first_outputs_2026-06-22_10-42-02/` contains **no baseline tables**.

**Fix:**
1. Add `table_encoder_baselines.csv` with mBERT, XLM-R, AraBERT, AfriBERTa, and a multilingual sentence-transformer baseline on the v68 dataset.
2. Add `table_heuristic_baselines.csv` with all-A, all-D, random, and length-matched corpus baselines.

### P1 — No single-generator vs. pool ablation
The paper claims "a multi-model generator pool is more robust than a single model," but the v68 outputs compare generators only descriptively (accuracy, HCW, fallback rate) without a controlled single-generator baseline.

**Fix:**
1. Run a single-generator ablation on 10 proverbs per language using only `gemma-4-31b-it` (the strongest generator).
2. Compare parse/fallback rates and HCW against the pooled result.

### P2 — No temporal or provider baselines
No comparison against older LLMs (GPT-3.5, Claude-2) or non-OpenRouter providers (Groq, Together, local models).

**Fix:** Add a "provider robustness" ablation if budget allows, or cite the legacy Groq numbers as a temporal baseline with explicit caveats.

---

## 8. Blinding / Audit Weaknesses

### P0 — Audit committee has severe position bias
`table5_position_bias.csv` shows consensus accuracy by position:
- A: **73.3%**
- B: 57.8%
- C: 48.9%
- D: **46.7%**

The correct-key distribution is balanced (45/45/45/45), but the **committee itself is not position-invariant**. When the correct answer is A, auditors agree 73.3% of the time; when it is D, only 46.7%. This means the audit signal is confounded by position, not just by shortcut content.

**Risk:** This is a fundamental audit flaw. Any metric derived from consensus accuracy (HCW, perfect consensus, consensus accuracy) is contaminated by position bias.

**Fix:**
1. **Report the position bias** explicitly in the paper as a committee-calibration finding.
2. **Mitigate in v70** by shuffling positions per item (the code already supports this; verify it is active).
3. **Down-weight** or **resample** A-position items when computing aggregate metrics, or use a position-corrected consensus score.

### P0 — Committee family diversity is weak
Current v68 audit pool: Meta (Llama), Mistral, Google (Gemma), DeepSeek. **No OpenAI, no Anthropic.** All four models are from different families, but the families are clustered (Google ×2 in generators, Google ×1 in auditors; Meta ×1 in auditors). This is weaker than the legacy committee that included OpenAI and Anthropic models.

**Fix:**
1. Add at least one OpenAI model (e.g., `openai/gpt-4o-mini`) and one Anthropic model (e.g., `anthropic/claude-sonnet-4`) to the audit starters when budget renews.
2. Report per-family accuracy breakdowns to check for shared failure modes.

### P1 — Individual auditor hit rates are not reported
The v68 report shows all four auditors have identical 56.7% accuracy because they are evaluated against consensus, not gold. But individual hit rates against the gold curated meaning are not computed.

**Fix:**
1. Compute and report per-auditor accuracy vs. `curated_meaning` (gold).
2. Report pairwise Cohen’s κ between auditors to measure agreement beyond chance.

### P2 — No human calibration of the committee
The LLM-proxy annotation (3 OpenRouter models) achieved Fleiss κ=0.67 against v68 consensus, but human annotators have not yet rated the 60-item sample.

**Fix:**
1. Complete the native-speaker human validation (60–90 items, 2–3 annotators per language).
2. Compute Cohen’s κ between human and consensus labels; report the calibration slope.

---

## 9. Position Bias and Length Bias Controls

### P0 — Position bias in audit committee (see Section 8)
This is the most critical bias issue. Key distribution is balanced, but committee behavior is not.

### P1 — Length parity exists but is not analyzed
The pipeline enforces ±35% / ±45% length parity, but the paper outputs do not report whether longer or shorter options are selected more often by auditors.

**Fix:**
1. Add a `table_length_bias.csv` showing mean option length by position and by consensus-correct vs. consensus-wrong items.
2. Report the correlation between length deviation and auditor selection.

### P1 — No option-shuffling robustness test
The code supports position shuffling, but the paper outputs do not include a shuffling ablation.

**Fix:**
1. Shuffle options 10 times for a 20-item subset.
2. Report mean accuracy, accuracy variance, and flip rate (how often the correct label changes position).

---

## 10. Generalization Claims vs. Actual Coverage

### P0 — Abstract overclaims cross-lingual generalization
The abstract states: `"English accuracy drops 8.9pp under S2, whereas Arabic and Yoruba drop only 2.2pp, suggesting that adversarial paraphrasing fails to transfer difficulty to morphologically complex and low-resource contexts."`

This claim is from the **legacy Pilot 2 S1/S2 pipeline (N=10, Groq)**, not from the current v68 distractor-generation data. The v68 data does not have an S1/S2 split in this form.

**Risk:** If the S1/S2 comparison is not re-run on the hardened pipeline, this is an unsupported generalization claim.

**Fix:**
1. **Do not include** the 8.9pp / 2.2pp cross-lingual boundary claim unless it is re-validated on the current pipeline.
2. If the paper is about distractor generation methodology, replace the S1/S2 claim with a **per-language distractor-quality analysis** (e.g., Arabic requires 1.52 fallback replacements vs. English 0.43).

### P0 — Scaling claims are aspirational
The abstract and memory mention scaling to N=15, N=700, and 100-item human validation. Only N=5 (180 MCQs) and a 60-item LLM-proxy validation exist.

**Fix:**
1. Remove all aspirational scaling claims from the abstract and introduction.
2. State the exact dataset size (180 MCQs) and validation size (60 items, LLM proxies; human validation pending).

### P1 — Generalization beyond proverbs is unsupported
The title mentions "low-resource figurative language," but the dataset covers only proverbs in three languages.

**Fix:**
1. Scope the generalization claim explicitly: "We study proverb understanding; extension to idioms, metaphors, and sarcasm is future work."
2. Do not claim cross-figurative-language generalization without data.

---

## 11. Other Reviewer-Attack Surfaces

### P0 — Failure taxonomy mixes legacy and current data
`table7_failure_taxonomy.csv` cites:
- Same-family exploitation: 31.1pp (legacy Groq)
- Chain-of-thought collapse: 34.7pp (legacy Groq)
- Multi-stage-prompt triviality: 100% (legacy Groq)
- Position bias: 60.6pp (legacy Groq)
- API/provider fragility: 90% (legacy Groq)
- Corpus fallback quality collapse: 43.9% (v68 current)

Five of six rows are from a different pipeline. Mixing them in one table without clear attribution is a reproducibility/authenticity issue.

**Fix:**
1. Split `table7` into `table7_legacy_findings.csv` and `table7_v68_findings.csv`.
2. In the paper, present the legacy findings as **prior art / motivation** and the v68 findings as **current contributions**.

### P0 — Unreleased code/data gap
The paper promises `"pipeline, audit logs, and dataset splits"` but the current repo contains:
- Source code ✅
- Audit logs ✅ (`openrouter_pilot1_test_output/`)
- Dataset splits ⚠️ Only the 180 MCQs and 60-item sample; the full 2,313 is not in the repo.

**Fix:**
1. Release the 180 MCQs with a clear license (CC BY 4.0 for English/Arabic; restricted or derivative-only for Yoruba).
2. Do not promise a larger release unless it exists.

### P1 — Yoruba data quality issues
The Yoruba inventory shows 3,834/3,974 rows with missing `QA_Flag` and 3,748 with missing `Comments`. This suggests the dataset was not fully QA-checked.

**Fix:**
1. Report the QA coverage rate: "X of 3,974 Yoruba proverbs passed QA flag."
2. Exclude or flag low-coverage items in the sampled 5-per-language set.

### P1 — Critical bug history erodes engineering credibility
The project has had multiple P0 bugs:
- S1 answer-key drift (76.7% mismatches)
- EOL model IDs (`claude-3.5-haiku`)
- Empty options in annotation pipeline
- Position bias in Pilot 2
- Budget exhaustion blocking v69/v70

While all were fixed, reviewers may question overall rigor.

**Fix:**
1. Add a "Known Limitations and Incident History" subsection documenting each bug, its fix, and the verification step.
2. Transparency about engineering challenges strengthens, not weakens, a methodology paper.

### P1 — LLM annotator refusal and reliability
The OpenRouter annotation run showed `gpt-4o-mini` refused 6/60 items (10%) and the earlier `gpt-4o` refused 60%. The Modal open-source run stalled due to cloud GPU capacity.

**Fix:**
1. Report refusal rates explicitly.
2. Use only models with <5% refusal for the final 4-model IAA.
3. Do not let LLM-proxy IAA substitute for human validation.

### P2 — No carbon or environmental reporting
The Elite Research Execution Plan mentions "cost, carbon, and compute budget" but no carbon estimates are in the paper outputs.

**Fix:** Add a `table_cost_carbon.csv` with API cost, estimated CO₂ (using OpenRouter/Middleware carbon estimators if available), and compute hours.

---

## Prioritized Fix List (P0 → P2)

| Priority | Gap | Owner | Effort | Impact |
|----------|-----|-------|--------|--------|
| **P0** | Abstract claims 2,313 MCQs; production is 180. Rewrite abstract immediately. | Author | 2h | Desk-reject avoided |
| **P0** | Legacy S1/S2 numbers (86.8% vs 62.5%) mixed into current paper. Remove or re-run. | Author | 4h | Authenticity restored |
| **P0** | Encoder baselines claimed in abstract but absent from outputs. Re-run or remove claim. | Author | 4h | Reproducibility restored |
| **P0** | Failure taxonomy mixes legacy and current data. Split tables. | Author | 2h | Authenticity restored |
| **P0** | Audit committee position bias (A=73.3% vs D=46.7%). Report + mitigate via shuffling. | Author | 4h | Core validity threat |
| **P0** | Yoruba copyright: no permission for Owomoyela 2005. Scope or seek permission. | Author | 8h | Legal/release risk |
| **P0** | DATA_PROVENANCE_TEMPLATE.md empty. Fill before submission. | Author | 4h | Submission requirement |
| **P0** | No statistical significance tests in outputs. Add McNemar/Wilcoxon + correction. | Author | 4h | Inferential rigor |
| **P0** | No environment lockfile. Pin requirements + add Dockerfile. | Author | 2h | Reproducibility |
| **P1** | Corpus fallback bottleneck unfixed (v69 blocked by budget). Renew budget or reframe paper. | Author | Budget-dependent | Core methodology |
| **P1** | Human validation incomplete (only LLM proxies, κ=0.67). Recruit native speakers. | Author | 2–4 weeks | Paper requirement |
| **P1** | 180 MCQs is small; scale to N=15 (540 MCQs) when budget renews. | Author | Budget-dependent | Benchmark adequacy |
| **P1** | Committee family diversity weak (no OpenAI/Anthropic). Add when budget renews. | Author | 2h | Audit robustness |
| **P1** | No length-bias, shuffling, or distractor-efficiency metrics. Add ablation tables. | Author | 6h | Methodology completeness |
| **P1** | Missing single-generator vs. pool ablation. Run 10-item controlled comparison. | Author | 4h | Main claim support |
| **P1** | English too easy (65% accuracy, 45% perfect consensus). Tighten NLI guard or add variant. | Author | 4h | Quality gate |
| **P1** | Arabic data provenance unclear. Document source dataset + license. | Author | 4h | Data licensing |
| **P1** | English scraping sources undocumented. Document URLs, dates, tools. | Author | 4h | Data licensing |
| **P1** | No per-model cost breakdown. Add cost_by_model.csv. | Author | 2h | Transparency |
| **P2** | No option-shuffling robustness test. Add 10-shuffle ablation. | Author | 4h | Robustness |
| **P2** | No carbon reporting. Add cost_carbon.csv. | Author | 2h | Completeness |
| **P2** | No CI check for notebook/source drift. Add pre-commit diff check. | Author | 2h | Maintenance |

---

## Recommended Paper Framing (Given Current State)

Given that v69/v70 are blocked by budget and human validation is pending, the **safest reviewer-proof frame** is:

> **"Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Methodology and Failure Taxonomy"**

**N=5 (180 MCQs) is acceptable IF:**
1. The abstract and claims are trimmed to match the actual data.
2. The failure taxonomy (corpus fallback → confident-wrong consensus, NLI over-filtering → partial items, position bias in audit committee, English triviality, Yoruba fragility) is the **central contribution**, not a limitation section.
3. Statistical tests and CIs are added.
4. Human validation (60–90 items) is presented as **in progress** with a timeline.
5. The encoder baselines and S1/S2 claims are either re-executed or removed.

**Do NOT submit a paper that:**
- Claims 2,313 MCQs when 180 exist.
- Mixes legacy Groq S1/S2 numbers with OpenRouter v68 numbers.
- Promises encoder baselines that are not in the released artifacts.
- Treats the 27.8% HCW and 43.9% partial+fallback rates as successes.
