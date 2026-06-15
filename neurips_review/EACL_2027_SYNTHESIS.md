# EACL 2027 Submission Assessment — ProverbGap v4.3.6

**Date:** 2026-05-24  
**Reviewers:** 3 (Multilingual NLP, Resources & Evaluation, Methodology)  
**Venue:** EACL 2027, Athens, Greece (March 9-14, 2027)  
**ARR Deadline:** August 3, 2026 (~10 weeks)

---

## The Bottom Line

| Metric | Score |
|--------|-------|
| **Current acceptance probability** | **~20%** |
| **With all fixes** | **~35-40%** |
| **Track fit** | Excellent (Resources & Evaluation) |
| **Time to deadline** | 10 weeks |
| **Feasibility** | Challenging but possible |

EACL 2027 is the **best target** for this paper. The multilingual/low-resource
angle is genuinely valued, and the R&E track is the right home. But the paper
has serious gaps that must be fixed in 10 weeks.

---

## The 5 Gaps (Ranked by Severity)

### Gap #1: ZERO Human Validation 🔴 FATAL

**All 3 reviewers flagged this.**

A benchmark claiming to test "cultural meaning comprehension" with zero
native speaker validation is not credible. EACL reviewers are particularly
sensitive to this for low-resource languages — they have seen too many
"African language" papers written by authors with no community connection.

**What you need:**
- 2 native speakers per language (6 total)
- 50 items per language validated
- Validation criteria: unambiguity, answerability, option uniqueness, cultural accuracy
- Inter-annotator agreement (Cohen's kappa)
- Cost: ~$300-500 on Prolific or Upwork
- Time: 2-3 weeks

**Without this: near-certain reject.**

---

### Gap #2: Data Provenance Unresolved 🔴 FATAL

| Language | Source | Status | Risk |
|----------|--------|--------|------|
| Yoruba | "A book" | NO license documented | Copyright violation |
| English | Web scraping | NO protocol documented | ToS violation |
| Arabic | HuggingFace | NO original dataset cited | Ethics violation |

ACL's 2024 Data Provenance Policy requires explicit documentation.
"From a book" and "web scraping" are automatic desk-reject triggers.

**What you need:**
- Yoruba: Identify the book. Get written permission OR replace with open data.
- English: Document scraping protocol (sites, rate, robots.txt, dedup).
- Arabic: Cite exact HF dataset, its license, and your modifications.
- Write a proper dataset card following the ACL DPI template.

**Without this: desk reject.**

---

### Gap #3: Only 1 Task (MCQ) 🟡 HIGH

Competitors have more tasks:
- ProverbEval: MCQ + FiB + Generation
- Jawaher: Translation + Explanation

A single-task benchmark feels thin. The paper's future work already
promises FiB and Generation — reviewers will ask why they're not included.

**What you need:**
- Add Fill-in-the-Blank task (uses existing data, ~1 week)
- Add Generation task ("Explain this proverb's meaning", ~2 weeks)
- Or: Frame the paper as "Phase 1: MCQ Benchmark" with FiB/Gen as future work

**Without this: weaker than competitors, but not fatal.**

---

### Gap #4: Single-Model Committee 🟡 HIGH

The paper reports a 2-model committee but only allam-2-7b is active
(llama-4 was dropped due to API failures). "Unanimous consensus" with
1 model is meaningless.

**What you need:**
- Add 2 more models (GPT-4o via OpenRouter, Claude via Anthropic, or
  a local model like Llama-3.3-70b)
- Or: Frame the evaluation as "pilot with 1 model, full committee in
  future work" (weaker but acceptable)

**Without this: methodology is underpowered.**

---

### Gap #5: No Human Baseline 🟡 HIGH

Without knowing human performance, model scores are uninterpretable.

**What you need:**
- 10 native speakers × 10 items per language = 300 evaluations
- Report human accuracy on S1 and S2
- Cost: ~$100-200 on Prolific
- Time: 1-2 weeks

**Without this: results lack calibration.**

---

## The Hidden Strength

All 3 reviewers independently praised the **negative results narrative**:
- API infrastructure collapse (769/790 failures)
- Same-family model exploitation
- CoT reasoning collapse (llama-4: 23/24 NaN)
- Think-tag parser bugs (qwen3-32b unclosed `<think>`)
- Rate-limit cascade dynamics

**No other benchmark paper documents real-world LLM evaluation failures
with this level of detail.** This is a genuine contribution that could
elevate the paper above "just another benchmark."

**Recommendation:** Expand the negative results section. Make it a
standalone contribution.

---

## 10-Week Action Plan to EACL 2027

| Week | Task | Critical? |
|------|------|-----------|
| 1 | Resolve data provenance (Yoruba book permission, English scraping protocol, Arabic HF citation) | 🔴 YES |
| 1-2 | Write dataset card | 🔴 YES |
| 2-3 | Hire native speakers, begin human validation (50 items × 3 languages) | 🔴 YES |
| 3-4 | Add human baseline (10 speakers × 10 items) | 🟡 HIGH |
| 4-5 | Implement FiB task | 🟡 HIGH |
| 5-6 | Expand committee to 3-4 models | 🟡 HIGH |
| 6-7 | Run full N=750 pipeline, generate all results | 🔴 YES |
| 7-8 | Write full paper (8 pages) | 🔴 YES |
| 8-9 | Internal review, revise based on feedback | 🟡 HIGH |
| 9-10 | Final polish, submit to ARR by August 3 | 🔴 YES |

**Total estimated cost:**
- Human validation: $300-500
- Human baseline: $100-200
- API calls for N=750: ~$50-100
- **Total: ~$450-800**

---

## Comparison: EACL 2027 vs Other Options

| Venue | Deadline | Fit | Acceptance (current) | Acceptance (fixed) |
|-------|----------|-----|----------------------|--------------------|
| **EACL 2027** | Aug 3, 2026 | ⭐⭐⭐⭐⭐ | ~20% | **~35-40%** |
| TACL | Rolling | ⭐⭐⭐⭐⭐ | ~25% | ~40-45% |
| NAACL 2027 | Dec/Jan | ⭐⭐⭐⭐ | ~20% | ~35-40% |
| ACL 2027 | Dec/Jan | ⭐⭐⭐⭐ | ~15% | ~30-35% |
| LREC 2028 | Oct 2027 | ⭐⭐⭐⭐⭐ | ~30% | ~45-50% |

EACL 2027 is the **best balance** of speed, fit, and prestige. TACL is
better for quality but has no deadline pressure. LREC 2028 gives the
most time but is farthest away.

---

## Final Recommendation

**GO for EACL 2027.** It is the right venue, the right track, and the
right timeline. But treat the next 10 weeks as a sprint:

1. **Week 1:** Fix data provenance (this is the hardest part)
2. **Weeks 2-3:** Human validation (this is the most important part)
3. **Weeks 4-6:** Add FiB task and expand committee
4. **Weeks 7-10:** Run pipeline, write paper, submit

The paper has genuine value — the Yoruba coverage, the meaning-comprehension
reframe, and the negative results are all real contributions. But they are
buried under unresolved data issues and missing validation. Fix those, and
this is a competitive EACL paper.
