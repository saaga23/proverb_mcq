# Mentor Document Verification Report

**Document under review:** `docs/ProverbGap_Mentor_Briefing.md`  
**Sources checked:** `memory.md`, `kaggle_analysis/Last_run/mcq-pass-shortcut.log`, `kaggle_analysis/Last_run/FINAL_AUDIT_v434.md`, `LITERATURE_BACKED_PLAN.md`, plus auxiliary project files (`DATASET_CARD.md`, `GENERATION_QUALITY_REPORT.md`, `audit_behavior_report.md`, `final_tables/table3_position_bias.csv`, `kaggle_analysis/input/mcq-pass-shortcut.log`).

---

## Em Dash Check

- **Em dash (—) count:** 0
- **Line numbers:** N/A
- **Status:** PASS. No em dash characters were found in the briefing.

---

## Historical Consistency Check

| Claim | Source Evidence | Verdict |
|-------|----------------|---------|
| **7,172 proverbs across 6 languages** | `DATASET_CARD.md` repeats the same figures, but the listed per-language counts (English 2,278 + Arabic 913 + Yoruba 3,931 + French 161 + German 142 + Spanish 63) sum to **7,488**, not 7,172. The `original_data/` CSVs are small samples (~100 rows each for EN/AR/YO), so they do not validate the full counts. | **MISMATCH / ARITHMETIC ERROR** |
| **Yoruba had 43.3% fallback in early runs** | `GENERATION_QUALITY_REPORT.md` (lines 61, 64, 125) confirms Yoruba Task B (Strategy 2) fallback of **43.3%** (13/30 items). | **CONFIRMED** |
| **Same-family exploitation (llama-4-scout + llama-3.3-70b)** | `memory.md` lines 23-26: generator `llama-4-scout-17b-16e-instruct` (Meta) and auditor `llama-3.3-70b-versatile` (Meta) scored **57.8%** on S2 vs **26.7%** on S1. | **CONFIRMED** |
| **Position bias 85.6% for A in pilot** | `memory.md` line 683 and `final_tables/table3_position_bias.csv` show position A accuracy of **85.56%** (S1) vs **64.4–66.7%** for B/C/D. | **CONFIRMED** |
| **GPU models failed** | `memory.md` lines 1172-1175: ALLaM-7B (auth/invalid), BLOOM-7B (OOM/bitsandbytes missing), AfroLLaMA (bitsandbytes missing). Later lines (1468-1469) also describe allam-7b-local as "degenerate" and afrollama as "suspicious." | **CONFIRMED** |
| **API providers failed** | `memory.md` lines 43-49 lists DeepInfra (402), SambaNova (500/404), Cerebras (404), NVIDIA (partial timeout). `audit_behavior_report.md` lines 71, 164 confirms Groq logged **15,131** HTTP 400 errors. | **CONFIRMED** |
| **Committee shrank from 5 to 2** | `memory.md` line 28 explicitly says "Committee Shrank from 5 → 3 Models." The final v4.3.4 run (`FINAL_AUDIT_v434.md`) uses **2** models. The briefing skips the intermediate 3-model stage. | **OVERSIMPLIFIED** |
| **v4.3.3 collapse (24.2% S1, 0.0% S2) & v4.3.4 recovery (86.8% S1, 62.5% S2)** | The v4.3.2 baseline (85.4% S1, 69.3% S2) and v4.3.4 recovery (86.8% S1, 62.5% S2) are confirmed in `memory.md` and `FINAL_AUDIT_v434.md`. **However**, the claimed v4.3.3 collapse numbers (24.2% S1, 0.0% S2) **do not appear in any project source**. The only catastrophic run with S2 ≈ 0.0% is **v4.1** (`kaggle_analysis/input/mcq-pass-shortcut.log`, run_20260521_215059), where S1 was ~14–15%, not 24.2%. No source links 24.2% to v4.3.3. | **UNVERIFIED / LIKELY FABRICATED** |
| **Runtime ~22 minutes** | `mcq-pass-shortcut.log` ends at **1320.2 s** (~22 min). `FINAL_AUDIT_v434.md` states "~22.0 min (1320.2 s)." | **CONFIRMED** |
| **Budget items and prices ($50 total)** | Prices (~$15 Groq Pro, ~$10 OpenRouter, ~$9 HF Pro, ~$10 Kaggle Plus, ~$5 DeepL) appear **only** in the briefing and `docs/ProverbGap_Paper_Draft.md`. No invoices, pricing screenshots, or cost spreadsheets exist in the project. | **UNVERIFIED ESTIMATES** |

### Summary of Inconsistencies
1. **Dataset size:** The per-language numbers sum to 7,488, contradicting the claimed total of 7,172. This error originates in `DATASET_CARD.md` and is copied into the briefing.
2. **v4.3.3 collapse:** The 24.2% / 0.0% figures are not supported by any log, audit, or memory file. They appear to conflate the v4.1 catastrophic run with the v4.3.3 label.
3. **Committee shrinkage:** The path was 5 → 3 → 2, not a direct 5 → 2 jump.

---

## AI-Detectability Check

The document is polished to the point of sounding like a template-generated executive summary. Specific red flags:

- **Generic framing:** "From Pilot to Scale: A Complete Journey" and "This document tells the full story: where we started, what broke, how we fixed it, where we are now, and what comes next" are hallmark AI-intro formulas.
- **Neat triadic lists:** Phrases like "same-family exploitation, API meltdowns, reasoning collapse" read like auto-summarized bullet clusters turned into prose.
- **Uniform chapter structure:** Every chapter follows an identical pattern (`**What we did:**` → `**What broke:**` → `**What we learned:**`). While readable, the mechanical regularity is a strong AI-detectability signal.
- **Lack of human color:** No specific dates, no direct quotes from team members, no idiosyncratic observations (e.g., "the model kept answering 'B' on Tuesdays"). The narrative is sanitized.

**Verdict:** Moderate-to-high AI-detectability. Recommend injecting informal asides, a specific anecdote, or a self-deprecating note to break the polished cadence.

---

## Tone Check

| Criterion | Assessment |
|-----------|------------|
| **Accessibility** | Good. The chapter structure creates a clear story arc, and the "What we learned" boxes help. |
| **Jargon explanation** | **Insufficient.** Terms such as *deterministic rotation*, *per-model shuffling*, *Jaccard similarity*, *McNemar test*, *bootstrap confidence intervals*, and *leakage heuristic* are used without plain-English definitions. A mentor from a non-NLP background may need footnotes or a glossary. |
| **Narrative clarity** | Strong. The progression from data collection → failures → fixes → current state → future work is logical. |
| **Mentor-appropriate detail** | The budget table (P0/P1/P2) and timeline are excellent. The technical deep-dives (e.g., API error codes) are interesting but could be moved to an appendix. |

**Verdict:** Good structural tone, but jargon density undermines accessibility for a non-technical mentor.

---

## Overall Verdict

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Em Dash Compliance** | ✅ PASS | Zero em dashes found. |
| **Historical Accuracy** | ⚠️ **PARTIAL FAIL** | Two significant errors: (1) dataset size arithmetic (7,172 vs 7,488), and (2) the v4.3.3 collapse narrative appears fabricated or conflated with v4.1. |
| **AI-Detectability** | ⚠️ **FLAG** | Polished, template-like phrasing throughout. Needs human anecdotes and irregular sentence rhythm. |
| **Tone for Mentor** | ⚠️ **FLAG** | Accessible structure, but unexplained jargon (McNemar, bootstrap, leakage heuristic) will lose non-expert readers. |

### Recommended Fixes Before Sending to Mentor
1. **Correct the dataset size claim.** Either update the total to 7,488 or verify and correct the per-language counts so they sum to 7,172.
2. **Clarify or remove the v4.3.3 collapse paragraph.** If referring to the v4.1 run, use the correct version label and the actual S1 figure (~14–15%). If the collapse truly happened under v4.3.3, provide the source log/audit.
3. **Add a "Jargon Quick-Reference" box** defining McNemar, bootstrap CI, leakage heuristic, and Jaccard similarity in 1 sentence each.
4. **Break the AI-polish** with one specific, informal anecdote (e.g., "We spent three hours debugging only to realize the model was outputting `<think>` tags").
5. **Footnote the budget estimates** so the mentor knows they are rough projections, not quoted prices.

**Bottom line:** The briefing is 70–80% accurate and well-organized, but the dataset arithmetic error and the unsupported v4.3.3 collapse story are serious enough that they must be corrected before the document is shared with a mentor or stakeholder.
