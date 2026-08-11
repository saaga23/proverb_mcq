# Reviewer #5 — Reproducibility, Threats to Validity, Writing & Completeness
## EACL 2027 ARR — ProverbGap

**Overall assessment:** The paper presents an interesting methodology, but it contains **fatal numerical errors in its primary results table**, **unexecuted experiments cited as empirical evidence**, and **systematic gaps in reproducibility documentation** that make it unsuitable for acceptance in its current form. The most damaging issue is that the headline metrics in Table 5.1 do not match the raw v68 output files — a reader who reproduces the counts from the released CSVs will find the paper's central claims are numerically wrong.

---

## (a) Severity-Graded Critique List

### REJECT

**R1. Primary results table contains incorrect headline metrics (§5.1, lines 187–189).**
- **Claimed:** HCW = 43.3%, hard fallback = 0.0%.
- **Actual from `pilot1_test_audit_results.csv`:** HCW = 50/180 = **27.8%** (consensus fraction ≥ 0.75 and consensus wrong).
- **Actual from `pilot1_test_generated_mcqs.csv`:** hard fallback (`length_fallback` status) = 29/180 = **16.1%**.
- The supporting artifact `table_bootstrap_cis.csv` also reports `hcw_rate = 0.4333` and `hard_fallback_rate = 0.0`, propagating the same error.
- The per-language report (`per_language_report.txt`) correctly computes 27.8% overall HCW but then incorrectly sums to 77/180 = 42.8%.
- **Impact:** Every downstream claim built on these numbers (failure taxonomy, cross-lingual asymmetry, cost-per-MCQ framing) is either overstated or understated. A reproducibility reviewer running `sha256sum -c` and then computing metrics from the CSVs will find the paper's main table is empirically false.

**R2. Unexecuted v69 LLM-fallback ablation cited as empirical evidence (§6.3, line 269).**
- §6.3 states: *"An LLM-based fallback generator (v69 ablation) is the highest-leverage fix."*
- Per the project run history (AGENTS.md), v69 was **budget-blocked** (`403 Budget limit exceeded`) and produced **no results**. There is no v69 dataset, no v69 analysis report, and no ablation comparison.
- **Impact:** This misrepresents the evidence base. The "highest-leverage fix" claim is speculative, not empirical. In a methodology paper, citing an unexecuted ablation as a finding is a cardinal sin.

**R3. The "production dataset" and "public testbed" claims are unsupported (§1, lines 18–23; §473).**
- The paper calls the 180 MCQ set a "public testbed" and a "production dataset" ($0.0047 per audited MCQ).
- Actual quality gates: HCW 27.8% (target <10%), partial+fallback 43.9% (target <15%), hard fallback 16.1% (target <5%), perfect consensus 41.7% (target <30%).
- Zero of the six shortcut-resistance gates pass. The dataset is demonstrably not production-ready.
- **Impact:** The framing is misleading. A testbed with 43.9% partial+fallback and 27.8% confident-wrong items is a failure analysis corpus, not a benchmark.

---

### MAJOR

**M1. §5.5 infrastructure robustness table conflates legacy API failures with v68 length-fallback status (lines 231–239).**
- The table compares "v58–v63 legacy" vs "v68 current" for hard fallback, claiming 0% for v68.
- In v58–v63, "hard fallback" meant API/provider crashes. In v68, "hard fallback" (`length_fallback`) means the length-parity gate rejected ≥2 distractors. These are categorically different failure modes.
- The 16.1% length_fallback rate is a pipeline calibration failure, not an infrastructure success. The table's 0% entry is therefore misleading.

**M2. §8.5 contradicts §5.2 on statistical significance of English vs. Arabic/Yoruba gap (lines 203 vs 389).**
- §5.2 (line 203): *"the 95% CIs overlap ... so the gap is not statistically distinguishable."*
- §8.5 (line 389): *"English vs. Arabic/Yoruba CIs barely overlap, suggesting a trend."*
- The actual overlap is substantial: English [53.3%, 76.7%] overlaps Arabic [40.0%, 65.0%] from 53.3% to 65.0% (11.7 pp overlap). This is not "barely overlap."
- **Impact:** The two sections reach opposite conclusions from the same data. The "suggesting a trend" language in §8.5 is also statistically incorrect — overlapping CIs do not "suggest a trend" in a frequentist framework.

**M3. Missing reproducibility parameters: temperature, decoding strategy, and retry policy (§3.7, §10.4).**
- The paper reports seed (`20260615`), model IDs, and cost, but **never states the temperature or top-p used for generation or audit**.
- For an LLM-as-judge audit, non-determinism is a first-class threat. Without temperature=0 (or reported values), the "reproducible" claim is hollow.
- The reproducibility checklist (lines 14–18) notes Docker and conda are "Not yet created," and `requirements.lock` is from the Kaggle environment only. Local reproduction is not guaranteed.

**M4. Gold meanings are LLM-generated (§4.2, line 141), but this circularity is not listed as a validity threat (§10).**
- The "correct" meanings are curated by `openai/gpt-4.1-nano` (line 141). The audit committee then judges distractors against these LLM-generated keys.
- This creates a **construct validity threat**: the gold standard is itself model-generated, potentially biasing the audit committee (which includes models from the same families) toward LLM-preferred phrasing.
- §10 lists corpus fallback, API fragility, and Yoruba copyright, but omits this fundamental circularity.

**M5. §6 mixes version ranges (v58–v69) but reports only v68 magnitudes, creating a false impression of longitudinal evidence.**
- §6 opening (line 245): *"six failure modes observed across v58–v69."*
- All magnitude bullets in §6 cite v68 numbers only (e.g., 43.9%, 27.8%, 36.3%).
- The failure taxonomy is presented as a cross-version synthesis, but it is a single-version snapshot with legacy labels.

**M6. The 60-item LLM-proxy IAA sample (§9) is unused and unreconciled with the v68 consensus labels.**
- §9.1 (line 397): The sample is *"stratified by generation status and consensus correctness for the planned human-validation study."*
- No human validation was performed. The IAA is reported as a standalone contribution but never connected to the v68 consensus labels to validate the audit committee.
- The sample sits in the paper as orphaned evidence.

**M7. The per-language report contains an arithmetic inconsistency that mirrors the main paper.**
- `per_language_report.txt` (lines 117–120): *"Overall HCW: 77/180 = 42.8%"*
- The per-language counts in the same file sum to 11 + 19 + 20 = **50** HCW items (27.8%), not 77.
- This suggests the report generation script has a bug, and the same bug likely produced the erroneous `table_bootstrap_cis.csv` and `table_single_generator_ablation.csv` values used in the paper.

---

### MINOR

**m1. §4.1 "5 × 12" notation (line 133) is correct but potentially confusing.**
- 5 proverbs × 3 generators × 4 variants = 60 MCQs. Writing "5 × 12" obscures the 3×4 structure and could be misread as 5 proverbs × 12 something.

**m2. §6.5 claims `overgenerate-select` has 71.1% fully generated (line 282), but Table 5.3 reports 60.0% for the same variant.**
- These are from different aggregations (variant-only vs. pooled), but the discrepancy is unexplained.

**m3. The reproducibility checklist (line 17) notes Docker is "Not yet created."**
- For a paper whose central contribution is reproducibility, shipping without a containerized environment is a missed opportunity.

**m4. §2.4 cites ProverbEval's 50% choice-order variance but does not connect it to the paper's own position-bias finding beyond a single sentence (line 53).**
- Given that position bias is one of the six documented failure modes, the connection to prior work is underdeveloped.

**m5. §10.3 (line 437) claims "180 MCQs (60 per language) is modest for per-language generalization claims," but §1 (line 21) frames the same 180 MCQs as a "public testbed."**
- The tension between "modest" and "testbed" is unresolved.

---

## (b) Enumerated List of Every Internal Contradiction

1. **§5.1 line 187 vs §6.3 line 266 vs §11 line 468:** HCW is reported as 43.3% in the main results table, 27.8% in the failure taxonomy, and 27.8% in the conclusion. The raw audit CSV confirms 27.8% is correct. The paper's primary results table is wrong.

2. **§5.1 line 189 vs raw data (`pilot1_test_generated_mcqs.csv`):** Hard fallback is reported as 0.0% in Table 5.1, but the generation status data shows 29/180 = 16.1% `length_fallback`.

3. **§5.1 line 189 vs §5.5 line 233:** Table 5.1 says hard fallback is 0.0% for v68; Table 5.5 also claims 0% for v68 by contrasting with legacy API failures. Both are wrong, and the comparison is category-confused.

4. **§5.2 line 203 vs §8.5 line 389:** §5.2 correctly states that English/Arabic/Yoruba CIs overlap and the gap is "not statistically distinguishable." §8.5 claims the CIs "barely overlap, suggesting a trend." The overlap is 11.7 percentage points (not "barely"), and "suggesting a trend" contradicts the earlier conclusion.

5. **§6 opening line 245 vs §6 magnitude bullets:** §6 claims the taxonomy covers "v58–v69," but every magnitude cited (43.9%, 27.8%, 36.3%, etc.) is from v68 only. The version range is overstated.

6. **§6.3 line 269 vs run history (AGENTS.md):** §6.3 cites "v69 ablation" as the highest-leverage fix, but v69 was budget-blocked and produced no data. The citation implies empirical validation that does not exist.

7. **§5.3 line 212 vs §6.3 line 266:** The pooled HCW in Table 5.3 is 43.3%, while §6.3 reports 27.8%. Both cannot be correct for the same 180 MCQs.

8. **`per_language_report.txt` lines 117–120 vs lines 15–17:** The report lists per-language HCW counts (English 11, Arabic 19, Yoruba 20) that sum to 50, but then states the overall HCW is 77/180 = 42.8%. The sum and the total contradict.

9. **`table_bootstrap_cis.csv` vs raw audit data:** The bootstrap CI file reports `hcw_rate = 0.4333` and `hard_fallback_rate = 0.0`, both of which contradict the raw CSV counts (27.8% and 16.1% respectively). This indicates a bug in the bootstrap or aggregation script that was not caught before publication.

10. **§1 line 15 vs §5.1 line 188:** §1 correctly states 43.9% partial+fallback, which matches both the raw data and Table 5.1. However, this highlights that only the HCW and hard-fallback rows in Table 5.1 are corrupted — the partial+fallback row is correct, making the two errors look like selective calculation bugs rather than random noise.

---

## (c) Single Most Lethal Reproducibility / Threat Issue

**The main results table (§5.1, lines 187–189) reports HCW = 43.3% and hard fallback = 0.0%, but the released v68 CSVs contain HCW = 27.8% and hard fallback = 16.1%.**

This is fatal for a reproducibility-focused review because:
- The paper's headline metrics are **numerically wrong** in the artifact that reviewers and readers will check first.
- The supporting CSVs (`table_bootstrap_cis.csv`, `table_single_generator_ablation.csv`) propagate the same errors, meaning the bug is not a isolated typo but a systematic calculation failure.
- The per-language report (`per_language_report.txt`) contains its own arithmetic inconsistency (summing to 77 instead of 50), suggesting the report-generation script has a bug that was never QA'd.
- The failure taxonomy (§6), cross-lingual analysis (§7), and conclusion (§11) all depend on these numbers. If the primary metrics are wrong, the entire evidential basis of the paper collapses.

**Concrete fix:** Recompute all bootstrap CIs and aggregate tables from the raw `pilot1_test_audit_results.csv` and `pilot1_test_generated_mcqs.csv` using the exact definitions in §4.3. Replace Table 5.1 with:
- HCW: **27.8%** (50/180), 95% CI [21.1%, 34.4%]
- Hard fallback: **16.1%** (29/180), 95% CI [10.6%, 21.7%]
- Partial + fallback: **43.9%** (79/180) — unchanged, already correct

Update `table_bootstrap_cis.csv`, `table_single_generator_ablation.csv`, and `per_language_report.txt` to match. Add a regression test that asserts aggregate metrics equal the raw CSV counts.

---

## Additional Recommendations for Authors

1. **Do not cite unexecuted ablations as evidence.** Recast §6.3 as a hypothesis ("We plan to replace the corpus sampler with an LLM fallback generator (v69/v70)") rather than an implication.
2. **Retire the "production dataset" language.** The dataset is a **methodology + failure-taxonomy artifact** with known quality issues. Frame it as such.
3. **Add temperature and decoding parameters to §3.7 and the reproducibility checklist.** Without these, the "reproducible" claim is unverifiable.
4. **List LLM-generated gold meanings as a construct-validity threat in §10.** The circularity of LLM-generated keys → LLM audit committee is non-trivial.
5. **Fix the per-language report generation script** and add CI that asserts aggregate counts equal the sum of per-language counts.
6. **Clarify §5.5's hard-fallback comparison.** Either (a) report v68 length_fallback as 16.1% and explain why it is not an "infrastructure failure" in the same sense as v58 API crashes, or (b) drop the legacy comparison and report v68 pipeline calibration metrics honestly.
7. **Resolve the §5.2 / §8.5 CI contradiction.** Delete the "suggesting a trend" language from §8.5 and note that overlapping CIs preclude significance claims.

---

*Review completed: 2026-07-12. All numerical claims verified against raw v68 output files in `kaggle/run_logs/v68/openrouter_pilot1_test_output/`.*
