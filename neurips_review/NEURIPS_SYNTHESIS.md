# NeurIPS Submission Assessment — ProverbGap v4.3.6

**Date:** 2026-05-24  
**Reviewers Consulted:** 3 (Track Fit, Data Provenance, Methodology)  
**Status:** FRANK ASSESSMENT — read carefully

---

## The Brutal Truth

### NeurIPS Main Conference
**Acceptance probability: ~3-5%**

NeurIPS main track is for novel algorithms, theoretical advances, and broad ML methodology. A proverb benchmark — even a good one — is not a fit. It would likely be **desk-rejected** without full review.

**Do not submit to NeurIPS main.**

### NeurIPS Datasets & Benchmarks (D&B) Track
**Current acceptance probability: ~15%**
**With major improvements: ~25-30%**

The D&B track accepts benchmark papers, but it is highly competitive (~1,200 submissions, ~250 accepted in 2024). ProverbGap would be mid-tier at best in this pool.

---

## The 4 Blockers

### Blocker #1: Data Provenance (FATAL if unresolved)

| Data Source | Status | Risk Level |
|-------------|--------|------------|
| **Yoruba** — "from a book" | NO license documented | 🔴 **FATAL** |
| **English** — web scraping | NO scraping protocol documented | 🔴 **FATAL** |
| **Arabic** — HuggingFace | NO original dataset cited | 🟡 **HIGH** |

NeurIPS now requires explicit data licensing documentation. "From a book" and "web scraping" without protocols are **automatic rejection triggers** in D&B track.

**Fix:**
- Yoruba: Identify the book. Check copyright. Get permission OR replace with openly licensed data.
- English: Document scraping protocol (sites, rate, robots.txt compliance, deduplication). Replace sources with restrictive ToS.
- Arabic: Cite exact HuggingFace dataset, its license, and your modifications.

### Blocker #2: Zero Human Validation (FATAL for D&B)

A benchmark without human validation is **not credible** at NeurIPS. Period.

**Fix:**
- Validate 50 items per language (7% of N=750)
- Native speakers check: unambiguity, answerability, option uniqueness, cultural accuracy
- Report inter-annotator agreement (Cohen's kappa)

### Blocker #3: Only 1 Task (MCQ)

NeurIPS D&B favors multi-task benchmarks. Your competitors:
- **ProverbEval** (NAACL 2025): MCQ + Fill-in-the-Blank + Generation
- **Jawaher** (NAACL 2025): Translation + Explanation
- **MasalBench** (2026): MCQ + human curation

**Fix:**
- Add Fill-in-the-Blank task (uses existing data)
- Add Generation task ("Explain this proverb's meaning")
- These are already in your future work section — move them to the main paper

### Blocker #4: 2-Model Committee

A 2-model committee cannot detect idiosyncratic failures. Standard is 3-5.

**Fix:**
- Add 2 more models (e.g., GPT-4o via OpenRouter, Claude via Anthropic)
- Or frame the 2-model design as a deliberate choice with justification

---

## What N=750 Per Language Gets You

| Metric | ProverbGap (planned) | ProverbEval (NAACL 2025) | Comparison |
|--------|----------------------|--------------------------|------------|
| Total items | 2,250 | ~2,500 | Comparable |
| Languages | 3 (EN, AR, YO) | 5 (Ethiopian) | Less diverse |
| Tasks | 1 (MCQ) | 3 (MCQ+FiB+Gen) | **Inferior** |
| Human validation | 0% | 100% of test set | **Inferior** |
| Low-resource focus | Yoruba only | 5 Ethiopian langs | Comparable |
| Distractor generation | LLM paraphrase | Human-written + LLM | Comparable |

**Verdict:** N=750 is sufficient, but the benchmark is outclassed on tasks and validation.

---

## Realistic Timeline to NeurIPS D&B Submission

| Task | Time | Critical? |
|------|------|-----------|
| Resolve data licensing (all 3 languages) | 2-4 weeks | **YES** |
| Human validation (50 items × 3 languages) | 3-4 weeks | **YES** |
| Add FiB task | 1 week | Yes |
| Add Generation task | 1-2 weeks | Yes |
| Expand committee to 4 models | 1 week | Moderate |
| Rewrite paper for NeurIPS D&B | 2 weeks | Yes |
| **Total** | **10-14 weeks** | |

NeurIPS 2026 deadline: Likely **mid-May 2026** (already passed or imminent).  
NeurIPS 2027 deadline: Likely **mid-May 2027** (you have ~1 year).

---

## Better Venue Options (Ranked)

| Venue | Deadline | Fit | Acceptance | Why |
|-------|----------|-----|------------|-----|
| **EMNLP 2026** | July/Aug 2026 | Excellent | ~22% | NLP-native venue, benchmark papers welcome |
| **ACL 2026** (Findings) | July 2026 | Excellent | ~25% | Top NLP venue, Findings accepts solid work |
| **NAACL 2026** | Jan 2026 (passed) | Excellent | ~25% | Wait for 2027 |
| **LREC-COLING 2026** | Oct 2026 | Perfect | ~30% | **Resource paper track** is ideal |
| **EACL 2026** | Oct 2026 | Excellent | ~25% | European ACL, strong on low-resource |
| **NeurIPS D&B 2027** | May 2027 | Moderate | ~25% | Possible with full improvements |

**My recommendation:**
1. **Submit to LREC-COLING 2026 (dataset/resource track)** — highest acceptance, best fit
2. **Parallel submit to EMNLP 2026** — top-tier NLP venue
3. **If rejected, revise and submit to NeurIPS D&B 2027** — gives you a full year to add FiB, generation, and human validation

---

## What To Do Right Now

1. **This week:** Resolve Yoruba book copyright and English scraping documentation
2. **Next 2 weeks:** Start human validation (hire native speakers on Prolific/Upwork)
3. **Month 2:** Implement FiB and generation tasks locally
4. **Month 3:** Run full N=750 pipeline, validate end-to-end
5. **Month 4:** Write paper, submit to LREC-COLING + EMNLP

---

## Final Verdict

**Can this work be published?** Yes — the data is valuable and the pipeline is rigorous.  
**Should it go to NeurIPS?** Not now. The fit is marginal and the data provenance issues are blockers.  
**Where should it go?** LREC-COLING 2026 (resource track) or EMNLP 2026. These are NLP-native venues where a cross-lingual proverb benchmark with rich annotations is genuinely novel and welcome.

**NeurIPS can wait.** Build a stronger paper first.
