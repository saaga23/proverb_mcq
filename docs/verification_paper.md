# Paper Draft Verification Report

**Document:** `docs/ProverbGap_Paper_Draft.md`  
**Run ID:** `run_20260523_224443` (v4.3.4)  
**Verifier:** AI-check sub-agent  
**Date:** 2026-05-24

---

## Em Dash Check

- **Count:** 0 actual em-dash characters (U+2014) found in the draft.
- The draft uses the Markdown convention `---` (three ASCII hyphens) in running prose. These render as em dashes in most Markdown processors but are technically valid source characters.
- **Status:** PASS *(with note: consider replacing `---` prose instances with `–` or `--` if the target venue requires strict Unicode punctuation)*

---

## Number Consistency Check

All numbers were cross-referenced against `kaggle_analysis/Last_run/mcq-pass-shortcut.log`, `kaggle_analysis/Last_run/evaluation_results.csv`, and `kaggle_analysis/Last_run/FINAL_AUDIT_v434.md`.

| Number | Expected | Found in Draft | Status |
|--------|----------|----------------|--------|
| S1 accuracy | 86.8% | 86.8% | PASS |
| S2-strict accuracy | 62.5% | 62.5% | PASS |
| S2 fallback rate | 21.3% (32/150) | 21.3% (32/150) | PASS |
| English S1 / S2 strict | 97.6% / 71.3% | 97.6% / 71.3% | PASS |
| Arabic S1 / S2 strict | 92.8% / 65.5% | 92.8% / 65.5% | PASS |
| Yoruba S1 / S2 strict | 70.0% / 46.2% | 70.0% / 46.2% | PASS |
| llama-4 S1 / S2 | 92.7% / 82.0% | 92.7% / 82.0% | PASS |
| allam-2-7b S1 / S2 | 82.9% / 50.0% | 82.9% / 50.0% | PASS |
| Bootstrap CI S1 | [84.3%, 89.2%] | [84.3%, 89.2%] | PASS |
| Bootstrap CI S2 strict | [58.1%, 66.6%] | [58.1%, 66.6%] | PASS |
| Position bias p (S1 / S2) | 0.739 / 0.746 | 0.739 / 0.746 | PASS |
| McNemar χ² (all / non-fb) | 131.3 / 110.8 | 131.3 / 110.8 | PASS |
| McNemar p-value | < 0.001 | < 0.001 | PASS |
| Encoder: afriberta S1 / S2 | 56.7% / 30.0% | 56.7% / 30.0% | PASS |
| Encoder: arabert S1 / S2 | 54.0% / 29.3% | 54.0% / 29.3% | PASS |
| Encoder: mbert S1 / S2 | 54.7% / 29.3% | 54.7% / 29.3% | PASS |
| Encoder: xlmr S1 / S2 | 55.3% / 36.0% | 55.3% / 36.0% | PASS |
| Runtime | ~22 min (~1,320 s) | ~22 min | PASS |
| MCQs generated | 300 | 300 | PASS |
| API evaluations | 1,500 | 1,500 | PASS |
| S2 fallback accuracy | 63.7% (log) | 63.7% | PASS |
| allam error rows | 221 (14.7%) | 221 (14.7%) | PASS |

**Minor discrepancies / notes:**
- The log header reads "v4.3.3" while the paper and audit report label the run "v4.3.4". The run ID (`run_20260523_224443`) and all metrics are identical; this is a cosmetic version-label mismatch only.
- The per-style CoT results (S1 89.3%, S2 55.3%) are mathematically correct but reflect **allam-2-7b only**, because CoT is skipped for llama-4-maverick (Section 4.5). The paper does not explicitly flag this in Table 5.5, which could mislead readers into thinking the average is across both models. **Suggested addition:** a footnote in the table stating "CoT averages reflect allam-2-7b only; llama-4-maverick CoT was excluded due to reasoning collapse."

---

## AI-Detectability Check

| Location | Issue | Suggested Rewrite |
|----------|-------|-------------------|
| **Line 32 (Related Work opening):** "Recent years have seen growing interest in proverb evaluation." | Overly generic, AI-template opening without a specific anchoring claim. | "Proverb understanding has attracted increasing benchmark attention, with concurrent work appearing at NAACL 2025 (ProverbEval, Jawaher) and CODI 2025 (PRONE)." |
| **Line 15 (Introduction):** "Proverbs represent one of the most challenging forms of figurative language for computational models." | Grandiose, unsourced superlative typical of AI-generated drafts. | "Proverbs are a long-recognized stress test for computational models because their meaning is culturally embedded and non-compositional (cite: any classic NLP textbook or survey)." |
| **Line 233 (Results, per-style):** "Zero-shot performs best, while few-shot shows lower accuracy---possibly due to the synthetic examples being too simplistic." | Hedging without evidence; the draft provides no analysis of why few-shot is lower. | "Zero-shot outperforms few-shot (Δ = 11.0 pp on S1, Δ = 16.0 pp on S2), suggesting that the synthetic in-context examples may have introduced surface-pattern leakage rather than genuine semantic guidance." |
| **Line 212 (Per-language):** Repetitive three-sentence structure ("English shows... Arabic performs... Yoruba exhibits...") | Repetitive parallel syntax is a common LLM artifact. | Vary sentence structure: "English dominates on both strategies, with the lowest fallback rate. Arabic maintains strong S1 performance but falls back on 20% of S2 items. Yoruba, by contrast, shows the largest S1–S2 gap and the highest fallback rate (36%), confirming that low-resource figurative language generation remains unreliable." |
| **Line 64 (Low-resource paragraph):** "AmharicStoryQA (2026)... EACL 2026... BEA 2025..." | Claims are made with venue-only citations and no author names, and **these three works do not appear in the References section**. | Either add full bibliographic entries for AmharicStoryQA, the EACL 2026 Egyptian-idiom paper, and the BEA 2025 shared task, or replace with fully cited references that are already in the bibliography. |

---

## Literature Consistency

| Citation (Draft) | Status | Notes |
|------------------|--------|-------|
| Alhazmi, A., et al. (2024). *EMNLP 2024*. | PASS | Matches project files (survey paper). |
| Azime, T., et al. (2025). *NAACL 2025 Findings*. | PASS | Matches memory.md. |
| Dubois, Y., et al. (2025). *EMNLP 2025 Findings*. | **FAIL — Title Mismatch** | Draft title: "Length-Controlled Generation for LLM Evaluation." The project sources do not list this exact title; the cited claim (nucleus sampling, detectability) is drawn from Dubois et al. (EMNLP 2025 Findings, arXiv:2510.13681) in memory.md, whose actual title is about detectability, not length control. **Fix:** Verify and replace with the correct title, or cite the correct Dubois paper. |
| Du, M., et al. (2022). *arXiv preprint*. | PASS | Matches LITERATURE_BACKED_PLAN.md BibTeX. |
| Fernandez, N., et al. (2024). *EMNLP 2024*. | PASS | Matches LITERATURE_BACKED_PLAN.md BibTeX. |
| Gales, M., et al. (2023). *Eval4NLP Workshop*. | PASS | Matches project sources. |
| Gu, L., et al. (2024). *arXiv preprint*. | PASS | Matches project sources. |
| Gurram, S., et al. (2026). *arXiv preprint*. | PASS | Matches project sources. |
| Gupta, A., et al. (2024). *arXiv preprint*. | PASS | Matches memory.md. |
| Krishna, K., et al. (2023). *NeurIPS 2023*. | PASS | Matches memory.md. |
| Maity, S., et al. (2024). *ECIR 2024*. | PASS | Matches memory.md. |
| Panickssery, A., et al. (2024). *NeurIPS 2024*. | PASS | Matches memory.md. |
| Sun, Y., et al. (2025). *CMU/Bosch*. | **FAIL — Venue Format** | Non-standard venue string. memory.md lists this as "CMU/Bosch 2025" (an institutional report). For an academic paper, either list the actual venue (arXiv or conference) or convert to a technical-report citation with institution name. |
| Yang, M., et al. (2025). *EMNLP 2025*. | PASS — with note | Draft uses short title; full title in LITERATURE_BACKED_PLAN.md adds "...An Analysis Using a Controlled Benchmark." Either is acceptable, but the full title is safer. |
| **Zhao, L.**, et al. (2025). *NAACL 2025*. | **FAIL — Wrong First Author** | Draft gives first author as **L. Zhao**. LITERATURE_BACKED_PLAN.md BibTeX and all project files list the first author as **Justin Zhao**. The draft title is also fabricated: "Heterogeneous Judge Pools Improve Ranking Robustness." The actual title is "Language Model Council: Democratically Benchmarking Foundation Models on Highly Subjective Tasks." **Fix:** Change author to "Zhao, J." and correct the title. |
| **Zheng, K.**, et al. (2024). *ICLR 2024 Spotlight*. | **FAIL — Wrong Title & Author** | Draft title: "Token and Position Bias in LLM Multiple-Choice Evaluation." memory.md (the project's canonical source) records this paper as **"Large Language Models Are Not Robust Multiple Choice Selectors"** (ICLR 2024 Spotlight). The first-author initial should be verified; the project does not confirm "K. Zheng." **Fix:** Replace with the exact title from memory.md and verify the author list against the official ICLR 2024 proceedings. |
| Zhou, Y., et al. (2024). *EMNLP 2024 Findings*. | PASS | Matches LITERATURE_BACKED_PLAN.md BibTeX. |

**Missing from References (cited inline but absent from the bibliography):**

1. **Joint Generation of Distractors (CMC 2025)** — cited Section 2.2.
2. **SEFD (PMC 2025)** — cited Section 2.2.
3. **SemEval 2025** — cited Section 2.2.
4. **Roundtable Policy (2025)** — cited Section 2.5.
5. **Jawaher (NAACL 2025)** — cited Section 2.1.
6. **PRONE (CODI 2025)** — cited Section 2.1.
7. **MasalBench (Kalhor et al., 2026)** — cited Section 2.1.
8. **D-GEN (ACL 2025)** — cited Section 2.2.
9. **DG Survey (2024)** — cited Section 2.2.
10. **Ackerman & Panickssery (ICLR 2025)** — cited Section 2.3.
11. **DISTO (EDM 2024)** — cited Section 4.2.
12. **AmharicStoryQA (2026)** — cited Section 2.6.
13. **EACL 2026** (Egyptian Arabic pragmatics gap) — cited Section 2.6.
14. **BEA 2025** — cited Section 2.6.

> **Action:** Add full bibliographic entries for all 14 missing references, or remove the inline citations if the works are non-essential.

---

## Overall Verdict: NEEDS REVISION

**Summary of required fixes before submission:**

1. **Literature (Critical):** Correct the Zhao et al. and Zheng et al. reference entries—both have wrong first authors and wrong/fabricated titles.
2. **Literature (Critical):** Add the 14 missing references that are cited inline but absent from the bibliography.
3. **Literature (Minor):** Fix Dubois et al. title mismatch; fix Sun et al. venue format.
4. **Transparency (Minor):** Add a footnote to Table 5.5 noting that CoT results are allam-2-7b only.
5. **Style (Minor):** Rewrite the generic opening of Section 2.1 and vary repetitive sentence structures in the per-language discussion.

**Strengths:** All empirical numbers are accurate and faithfully reproduced from the v4.3.4 run artifacts. The statistical tests, confidence intervals, and per-breakdown tables show no computational errors.
