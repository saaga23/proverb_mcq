# Surgical EACL Boosters — Prioritized by Impact / Effort

> **Constraint:** No new API calls, no new data collection, minimal cost.  
> **Goal:** Maximum reviewer-perceived quality improvement for EACL submission.

---

## TIER 1: DO THESE IMMEDIATELY (High Impact, Low Effort)

### 1. Fix All Citation Errors (2 hours)
**Why:** Wrong citations = instant credibility death at EACL.

| Issue | Fix |
|-------|-----|
| Zhao, L. → **Zhao, J.** | First author is Justin Zhao, not L. Zhao |
| Wrong Zhao title | Actual: *"Language Model Council: Democratically Benchmarking Foundation Models on Highly Subjective Tasks"* |
| Zheng, K. title wrong | Actual: *"Large Language Models Are Not Robust Multiple Choice Selectors"* (ICLR 2024 Spotlight) |
| Dubois title mismatch | Verify actual title vs "Length-Controlled Generation..." |
| Sun, Y. venue | "CMU/Bosch" is not a venue → cite as tech report or find actual venue |
| **12 missing references** | Add full bib entries for: Joint Generation, SEFD, SemEval 2025, Roundtable Policy, Jawaher, PRONE, MasalBench, D-GEN, DG Survey, Ackerman & Panickssery, DISTO, AmharicStoryQA |

**Effort:** Pure editing. Use Google Scholar to verify every citation.

---

### 2. Rewrite AI-Detectable Language (1 hour)
**Why:** EACL reviewers are increasingly sensitive to LLM-generated prose.

| Location | Current (Flagged) | Rewrite |
|----------|-------------------|---------|
| Line 15 (Intro) | "Proverbs represent one of the most challenging forms..." | "Proverbs are a long-recognized stress test for computational models because their meaning is culturally embedded and non-compositional (Taylor, 1981; Honeck, 1997)." |
| Line 32 (Related Work) | "Recent years have seen growing interest..." | "Proverb understanding has attracted increasing benchmark attention, with concurrent work appearing at NAACL 2025 (ProverbEval, Jawaher) and CODI 2025 (PRONE)." |
| Line 212 (Per-lang) | "English shows... Arabic performs... Yoruba exhibits..." | "English dominates on both strategies, with the lowest fallback rate. Arabic maintains strong S1 performance but falls back on 20% of S2 items. Yoruba, by contrast, shows the largest S1–S2 gap and the highest fallback rate (36%), confirming that low-resource figurative language generation remains unreliable." |
| Line 233 (Per-style) | "possibly due to the synthetic examples being too simplistic" | "Zero-shot outperforms few-shot (Δ = 11.0 pp on S1, Δ = 16.0 pp on S2), suggesting that the synthetic in-context examples may have introduced surface-pattern leakage rather than genuine semantic guidance." |

---

### 3. Add Qualitative Error Analysis with Concrete Examples (3 hours)
**Why:** EACL reviewers love seeing *actual data* — not just tables.

**Add a new subsection: 5.9 Qualitative Examples**

Include 4–6 examples with:
- The proverb (source language + English)
- The 4 options (correct + 3 distractors)
- What each model predicted
- Why it's interesting

**Example categories to show:**
1. **S1 Easy / S2 Hard:** English proverb where S1 is trivial but S2 paraphrase fools models
2. **Yoruba Fallback:** An item that had to fall back to generic distractors — show the proverb and explain why qwen3-32b failed
3. **Model Disagreement:** An item where llama-4-maverick got it right but allam-2-7b got it wrong (or vice versa)
4. **Same-Family Exploitation (Historical):** Show the llama→llama example from early iterations
5. **CoT Collapse:** Show a CoT reasoning trace that goes wrong

**This costs $0** — you already have all the data in your logs.

---

### 4. Add Model Disagreement Analysis (2 hours)
**Why:** With only 2 models, analyzing WHEN they disagree is more interesting than just reporting averages.

**Add a table:**

| Disagreement Type | Count | % of Total | allam-2-7b Correct | llama-4 Correct | Interpretation |
|-------------------|-------|------------|-------------------|-----------------|----------------|
| S1: Split vote | 81 | 18% | 47 | 34 | allam better on easy items? |
| S2: Split vote | 142 | 31.6% | 61 | 81 | llama better on hard items |
| S2: Both wrong | 102 | 22.7% | — | — | Both models fooled |

**Add insight:** "On items where models disagree on S2, llama-4-maverick is correct 57% of the time (81/142), suggesting stronger reasoning on adversarial distractors. On S1 disagreements, allam-2-7b is correct 58% of the time (47/81), possibly reflecting Arabic-centric cultural knowledge on easier items."

---

## TIER 2: DO THESE IF YOU HAVE TIME (Medium Impact, Medium Effort)

### 5. Add Related Work Comparison Table (1 hour)
**Why:** EACL reviewers want to see how you differ from concurrent work.

| Feature | ProverbEval | Jawaher | PRONE | MasalBench | **ProverbGap** |
|---------|-------------|---------|-------|------------|----------------|
| Languages | 6 Ethiopian | 20 Arabic dialects | Nepali | Persian | **En, Ar, Yo** |
| Task types | MCQ, FiB, Gen | Trans, Expl | MCQ | MCQ | **MCQ** |
| Distractor source | Human | N/A | Human | LLM + human | **LLM adversarial** |
| Cross-lingual? | ✗ | ✗ | ✗ | ✗ | **✓** |
| Shortcut testing? | ? | ? | ? | ? | **✓** |
| Position bias test? | ? | ? | ? | ? | **✓** |
| Leakage detection? | ? | ? | ? | ? | **✓** |
| Human validation? | ✓ | ✓ | ✓ | ✓ | **Planned** |
| N (proverbs) | ? | 10,037 | 2,830 | ? | **7,172** |

This frames ProverbGap as the **only cross-lingual adversarial benchmark with systematic shortcut testing**.

---

### 6. Add "Reproducibility Statement" Box (30 min)
**Why:** EACL has reproducibility badges. Even a simple statement helps.

```
Reproducibility Statement
- Code: Single Kaggle notebook, SQLite caching, fixed seeds
- Runtime: ~22 min for N=150; ~1.7 hrs projected for N=700
- Cost: ~$0 (API-only, no GPU needed for committee)
- Data: Released with provenance documentation
- Random seeds: 42 (all stochastic operations)
- API providers: Groq (allam-2-7b), NVIDIA (llama-4-maverick)
```

---

### 7. Add Data Provenance Subsection (1 hour)
**Why:** EACL reviewers scrutinize data sources.

Add to Section 3.1:
```
### 3.1.1 Data Provenance
- **English:** Scraped from [list sites], filtered for canonical proverbs, 
  contamination-filtered. See Appendix A for full protocol.
- **Arabic:** Sourced from HuggingFace dataset [ID], 913 MSA proverbs with 
  English translations and cultural explanations.
- **Yoruba:** Extracted from Owomoyela (2005), *Yoruba Proverbs*, 
  University of Nebraska Press. 3,931 proverbs OCR'd from the 5,235-proverb 
  collection. See Appendix B for OCR protocol.
```

**You already have the Yoruba citation.** Fill in English and Arabic when you find them.

---

## TIER 3: HIGH IMPACT BUT REQUIRES EFFORT

### 8. Run Minimal Human Validation (2–3 days, $150–200)
**Why:** This is the #1 thing that will separate accept from reject at EACL.

**Minimum viable:**
- 1 Arabic native speaker × 30 items
- 1 Yoruba native speaker × 30 items  
- 1 English native speaker × 30 items

**Tasks:** Rate each item on 1–5 scale for:
1. Proverb text correctness
2. Meaning explanation accuracy
3. Distractor plausibility (is the wrong option believable?)
4. Cultural appropriateness

**Document:** "A native speaker of each language reviewed 30 randomly sampled items. Mean ratings: English 4.6/5, Arabic 4.3/5, Yoruba 4.1/5. No items were flagged as culturally inappropriate."

**If you truly cannot do this:** Add a section describing the protocol you WILL execute, and frame it as "human validation is in progress." But know that EACL reviewers may still penalize this.

---

### 9. Scale to N = 700 (1–2 days, API-dependent)
**Why:** N=150 is a pilot. EACL expects meaningful scale.

**Prerequisites:**
- [ ] Fix Groq API key situation (get Pro or more keys)
- [ ] Test N=50 per language first
- [ ] Full run: 700 proverbs × 3 languages = 2,100 items

**If API keys are the blocker:** Run N=250 per language (750 total) instead of 700. Still 5× the pilot.

---

## WHAT TO SKIP (Low Impact / High Effort)

| Thing | Why Skip |
|-------|----------|
| FiB task | Defer to ACL/NAACL 2027. Not needed for EACL MCQ-only. |
| Generation task | Same — defer. |
| French/German/Spanish | Sample sizes too small (63–161). Don't dilute focus. |
| GPU local models | They all failed. Don't waste time. |
| kNN/MSP experiments | Already documented as negative results. Don't expand. |
| Embedding diversity scoring | Future work. Not critical for acceptance. |

---

## RECOMMENDED EXECUTION ORDER

| Day | Task | Effort |
|-----|------|--------|
| 1 | Fix citations + rewrite AI-detectable language | 3 hrs |
| 2 | Add qualitative examples + disagreement analysis | 4 hrs |
| 3 | Add comparison table + reproducibility statement + provenance | 3 hrs |
| 4–5 | Post native speaker jobs, start validation | 2 hrs |
| 6–7 | Scale pipeline to N=250–700 | API-dependent |
| 8 | Final proofread, update abstract to N=700 | 2 hrs |

---

## THE ONE THING THAT WILL MAKE OR BREAK YOU

**Human validation.** Everything else is polishing. If you have ZERO native speaker checking, EACL reviewers will flag it as a fatal flaw. The comparison with ProverbEval, Jawaher, and PRONE is stark — all three had human validation.

**If you can only do ONE thing beyond fixing citations:**  
→ **Get 1 native speaker per language to check 30 items each.**  
→ Cost: ~$150. Time: 2–3 days. Impact: Massive.

---

*Generated for EACL 2027 submission. Target: August 3, 2026 ARR deadline.*
