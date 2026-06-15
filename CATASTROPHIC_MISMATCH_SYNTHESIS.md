# CATASTROPHIC DATA MISMATCH — SYNTHESIS REPORT
## ProverbGap MCQ Pipeline v4.3.5 — Emergency Review

**Date:** 2026-05-24
**Status:** CRITICAL — Data-model mismatch discovered in actual_data/
**Agents consulted:** 8 (2 data analysts + 4 conference reviewers + 2 lab researchers)

---



======================================================================
SOURCE: phase1_agent_A.txt
======================================================================

======================================================================
PHASE 1A: ENGLISH & ARABIC DATA STRUCTURE ANALYSIS
======================================================================

--- ENGLISH CLEANED ---
Shape: (2278, 3)
Columns: ['Sample_ID', 'Proverb', 'Correct_Meaning']
Missing: {'Sample_ID': 0, 'Proverb': 0, 'Correct_Meaning': 0}
Duplicate Proverbs: 0

Proverb len  -> mean=33.1 median=32 max=125
Meaning len  -> mean=74.7 median=67 max=445

Meaning contains proverb text: 76/2278 (3.3%)

--- 5 SAMPLE ROWS ---

[0] Proverb: A bird in the hand is worth two in the bush
     Meaning: The proverb 'A bird in the hand is worth two in the bush' means that it's better to hold onto something you have rather than take the risk of getting something better which may come to nothing.

[50] Proverb: Cold feet
     Meaning: To 'get cold feet' is to become disheartened or timid, losing one's previous enthusiasm or courage.

[200] Proverb: Take the gilt off the gingerbread
     Meaning: Remove an item's most attractive qualities.

[500] Proverb: Courtesy is contagious
     Meaning: If you are polite to other people, they will be polite to you.

[1000] Proverb: Of two evils choose the lesser
     Meaning: When you have a choice to make and neither option is attractive, choose the one that is less damaging or costly.

======================================================================
--- ARABIC CLEANED ---
Shape: (913, 4)
Columns: ['Sample_ID', 'source_text', 'english_translation', 'Cultural_Context']
Missing: {'Sample_ID': 0, 'source_text': 0, 'english_translation': 0, 'Cultural_Context': 0}

Source len      -> mean=26.1 median=24
Translation len -> mean=34.4 median=31
Cultural len    -> mean=153.2 median=113
Cultural NULL   -> 0

--- 5 SAMPLE ROWS ---

[0] AR: آخر الحياة الموت
     EN:  Live life to its fullest; Tempus fugit, utere.
     CC: A wisdom that has become a proverb about not caring about threats. 

[20] AR: إلى حتفي مشت قدمي.
     EN: I dug my own grave.
     CC: A short phrase that means I strove with all my will to an end that I discovered I had chosen for myself.

[100] AR: ما خاب من استشار.
     EN: Advice is ever in want.
     CC: The proverb means that it is wise and sensible to seek advice from others in cases of uncertainty related to making a decision or embarking on a new e

[300] AR:   أكلب الكدرة أعلى فمها الطفلة تتبع أمها
     EN: Like mother, like daughter.
     CC: The proverb means that the daughter always resembles the mother in her morals and behavior.

[500] AR: الكوكه تعايب على أم زِرْ
     EN: Let he who is without sin cast the first stone.
     CC: This proverb refers to the woman who criticizes people even though she has many flaws, like an ugly woman (Kuka) who criticizes someone a one-eyed wom

--- TRANSLATION vs CULTURAL_CONTEXT COMPARISON ---
Rows with both: 913/913

Trans:  Live life to its fullest; Tempus fugit, utere.
Cult:  A wisdom that has become a proverb about not caring about threats. 

Trans: Sticks to them like a shadow.
Cult:  The proverb refers to someone who follows another person more than his shadow follows him.

Trans: Kindness begets kindness.
Cult:  It means that kindness and good treatment are the only way to gain people's love.

======================================================================
KEY FINDING: English 'Correct_Meaning' is an EXPLANATION, not a translation.
The pipeline used this as if it were a translation. This is WRONG.
Arabic has BOTH translation and Cultural_Context — richer but unused.



======================================================================
SOURCE: phase1_agent_B.txt
======================================================================

======================================================================
PHASE 1B: YORUBA DATA STRUCTURE ANALYSIS
======================================================================
Shape: (3974, 7)
Columns: ['Sample_ID', 'Source_Text_Yo', 'Target_Text_En', 'Cultural_Context', 'Provenance', 'QA_Flag', 'Comments']
Missing per column:
Sample_ID              0
Source_Text_Yo         0
Target_Text_En         1
Cultural_Context       2
Provenance             0
QA_Flag             3834
Comments            3748
dtype: int64
Duplicate Source_Text: 2

Source_Text_Yo len -> mean=44.0 median=39 max=308

Target_Text_En len -> mean=84.4 median=75 max=394

Cultural_Context len -> mean=64.6 median=60 max=215

QA_Flag values:
QA_Flag
FIX        88
DROP       39
PERFECT    13
Name: count, dtype: int64

Provenance top 10:
Provenance
part2.docx    671
part1.docx    612
part5.docx    602
part3.docx    586
part4.docx    535
part6.docx    513
part7.docx    445
Unknown        10
Name: count, dtype: int64

Rows with Comments: 226
Sample comments:
  - Fix space in the target_text_en "but tucks"
  - Fix space in the target_text_en "pres ence"
  - Fix space in the cultural_context "dis charge"
  - Removed hyphen in the target_text_en "Mokú-ṣiré’s". it was absent in the original yoruba text
  - in the yoruba text i can see "ngo" instead of "n o". This is an old way of wrting it. should it be r
  - Added "full stop" to the end of Source_Text_Yo
  - Added "full stop" to the end of Source_Text_Yo
  - Added "full stop" to the end of Source_Text_Yo
  - Removes hyphen from cultural context "mis-takenly"
  - Removed space from "there fore" in cultural context

Rows with BOTH translation and cultural context: 3971/3974

--- 5 SAMPLE ROWS ---

[0] Yoruba: A di gàárì sílẹ́ ewúrẹ́ ńyọjú; ẹrù ìran rẹ́ ni?
     Trans:  We prepare the saddle, and the goat presents itself; is it a burden for the lineage of goats?
     Cult:   Goats that know their place do not offer their backs to be saddled.
     Prov:   part1.docx
     QA:     PERFECT

[100] Yoruba: Àgbà tó bú ọmọdé fi èébú-u rẹ̀ tọrọ.
     Trans:  An elder who insults a youth makes a present of his own insult.
     Cult:   Only those who show respect for others may expect respect in return. Compare the preceding and following entries.
     Prov:   part1.docx
     QA:     FIX

[500] Yoruba: A kì í fi ẹran ikún gbọn ti àgbọ̀nrín nù.
     Trans:  One does not brush off antelope meat with squirrel meat.
     Cult:   Never prefer something of little value to something of great value.
     Prov:   part1.docx
     QA:     nan

[1000] Yoruba: Ṣà ǹgbákó ró, a ní kò róo re, Ṣàǹgbàkù-ú gbè é lẹ́sẹ̀.
     Trans:  Ṣàǹgbákó makes a sound and we say the sound is foul, and then Ṣàǹgbàkù lends its voice in its support.
     Cult:   Do not choose to do things that others before you have been condemned for doing.
     Prov:   part2.docx
     QA:     nan

[2000] Yoruba: Abánigúnwà ní ḿmọ ìjagun ẹni.
     Trans:  It is he who shares one’s throne that knows one’s strategy in battle.
     Cult:   Only soulmates know each other’s minds.
     Prov:   part4.docx
     QA:     nan

Of first 100 with both: 0 have near-identical trans+cult text

======================================================================
KEY FINDING: Yoruba has 7 rich columns including Cultural_Context,
Provenance, QA_Flag, Comments. The pipeline used only Proverb+Translation.
QA_Flag can filter quality. Cultural_Context enables meaning-comprehension tasks.



======================================================================
SOURCE: phase2_reviewer_ACL.txt
======================================================================

================================================================================
PHASE 2A: ACL/EMNLP REVIEWER #1 — TASK VALIDITY & METHODOLOGY CRITIQUE
================================================================================

Reviewer Profile: Senior ACL/EMNLP reviewer, 15+ years in benchmark design,
figurative language evaluation, and low-resource NLP. Has reviewed ProverbEval,
MMLU-Pro, and HELM.

---

CRITICAL FLAW #1: DATA-MODEL MISMATCH (FATAL)
----------------------------------------------

The paper claims to evaluate "proverb understanding" but the gold standard for
English is `Correct_Meaning` — an EXPLANATION of the proverb's wisdom — while
the pipeline treats it as a TRANSLATION.

Evidence from data analysis:
- English "Correct_Meaning" mean length = 74.7 chars (explanation prose)
- Example: "Cold feet" → "To 'get cold feet' is to become disheartened or timid..."
- The S2 generator was prompted: "Correct English translation: {translation}"
  But the text fed into that slot was the MEANING, not a translation.

Consequence: The model-generated "paraphrase" is paraphrasing an EXPLANATION,
but the prompt told it to paraphrase a TRANSLATION. The semantic gate
(Jaccard ≥ 0.25) checked similarity to the meaning text, but the length gate
enforced similarity to explanation length, not translation length.

Reviewer verdict: This is NOT a translation comprehension benchmark. It is a
meaning-explanation benchmark that was mistakenly built with translation
infrastructure. The task formulation is internally inconsistent.

RECOMMENDATION: The authors must either:
(a) Reframe the ENTIRE paper as "proverb meaning comprehension" and redesign
    prompts to ask "What does this proverb mean?" rather than "What is the
    correct translation?"
(b) Obtain actual English translations and rebuild the pipeline around them.

---

CRITICAL FLAW #2: ARABIC GOLD STANDARD IS AMBIGUOUS
----------------------------------------------------

Arabic has BOTH `english_translation` AND `Cultural_Context` for all 913 items.
The pipeline used... neither correctly. The column mapper aliased
`english_translation` → `proverb_en`, but the evaluation prompt asks
"What is the correct meaning/translation?" — conflating two distinct tasks.

The Cultural_Context (mean 153 chars) is substantively different from the
translation (mean 34 chars). Using translation as the gold standard when
Cultural_Context exists is a missed opportunity AND a methodological error.

Reviewer question: Which column was the "correct answer" in the MCQ?
- If `english_translation`: The task is translation matching.
- If `Cultural_Context`: The task is meaning comprehension.
- The paper cannot have it both ways without clearly distinguishing.

---

CRITICAL FLAW #3: YORUBA QA FLAGS IGNORED
------------------------------------------

Yoruba has 3,974 proverbs with QA_Flag values:
- FIX: 88 items (known errors)
- DROP: 39 items (should be excluded)
- PERFECT: 13 items
- NULL: 3,834 items (unreviewed)

The pipeline sampled 50 items without checking QA_Flag. If DROP items were
included, the benchmark contains known-bad data. If FIX items were included,
the benchmark contains known-flawed data.

Reviewer verdict: Any benchmark that includes known-bad items is not
reviewable. The authors must filter by QA_Flag (exclude DROP, review FIX)
before any claims about Yoruba quality can be taken seriously.

---

CRITICAL FLAW #4: NO HUMAN VALIDATION OF GENERATED ITEMS
---------------------------------------------------------

The paper reports N=150 pilot with 21.3% fallback rate. A 21% fallback means
1 in 5 items has placeholder distractors ("Incorrect alternative"). These items
are trivially easy for any model. Including them in accuracy calculations
inflates the denominator and distorts the S1 vs S2 gap.

Reviewer question: Were ANY of the 150 items human-validated for:
- Unambiguity? (Is there exactly one correct answer?)
- Answerability? (Can a human familiar with the language answer it?)
- Option uniqueness? (Are distractors semantically distinct?)

Without human validation, the 62.5% S2 accuracy could reflect bad items,
not genuinely hard distractors.

---

CRITICAL FLAW #5: POSITION BIAS CLAIM IS UNTESTED
--------------------------------------------------

The paper claims "position bias is effectively mitigated" via seeded shuffling.
But there is no ablation: no comparison of accuracy when correct answer is
always A vs. always D vs. shuffled. The claim is asserted, not demonstrated.

---

POSITIVE ASPECTS (to be fair)
------------------------------
1. The contamination filter is a good defensive practice.
2. Pre-flight health checks prevent silent model failures.
3. The two-strategy design (easy baseline + hard adversarial) is sound in
   principle.
4. Cross-family generator (qwen3) vs. committee (llama-4, allam) is correct.

---

OVERALL RECOMMENDATION: REJECT (major revision required)
---------------------------------------------------------

The paper has a fundamental data-model mismatch that invalidates the task
formulation. Before resubmission, the authors must:
1. Clarify whether the task is translation matching OR meaning comprehension
2. Use the correct column for each language as the gold standard
3. Filter Yoruba by QA_Flag
4. Human-validate at least 30 items per language
5. Add position bias ablation
6. Report accuracy EXCLUDING fallback items (or report fallback separately)

Estimated revision time: 4–6 weeks.



======================================================================
SOURCE: phase2_reviewer_NAACL.txt
======================================================================

================================================================================
PHASE 2B: NAACL REVIEWER #2 — LOW-RESOURCE & CULTURAL VALIDITY CRITIQUE
================================================================================

Reviewer Profile: NAACL reviewer specializing in African NLP, Arabic NLP,
and culturally situated language evaluation. Reviewed MasalBench, Jawaher,
AmharicStoryQA. Native Yoruba speaker.

---

CRITICAL FLAW #1: YORUBA CULTURAL CONTEXT IS THE REAL GOLD STANDARD
--------------------------------------------------------------------

Yoruba data has three text columns:
- Source_Text_Yo: The proverb in Yoruba
- Target_Text_En: English translation (often literal, sometimes awkward)
- Cultural_Context: The actual cultural meaning/wisdom (mean 64.6 chars)

Example from data:
  Proverb: "A di gàárì sílẹ́ ewúrẹ́ ńyọjú; ẹrù ìran rẹ́ ni?"
  Translation: "We prepare the saddle, and the goat presents itself; is it
                a burden for the lineage of goats?"
  Cultural_Context: "Goats that know their place do not offer their backs
                     to be saddled."

The Cultural_Context is what a Yoruba elder would tell you the proverb MEANS.
The Target_Text_En is a linguist's literal rendering. The pipeline used
Target_Text_En as the gold standard. This is backwards.

For a benchmark of "proverb understanding," the Cultural_Context should be
the correct answer. Using the literal translation tests translation skill,
not proverb comprehension. A model could match "goat" + "saddle" without
understanding "know your place."

Reviewer verdict: The Yoruba evaluation is culturally invalid. It tests
lexical translation, not proverbial wisdom.

---

CRITICAL FLAW #2: ARABIC CULTURAL CONTEXT IS RICHER THAN TRANSLATION
---------------------------------------------------------------------

Arabic Cultural_Context (mean 153 chars) vs. english_translation (mean 34 chars):

  Translation: "Sticks to them like a shadow." (5 words)
  Cultural_Context: "The proverb refers to someone who follows another person
                     more than his shadow follows him." (19 words)

The translation is a pithy equivalent. The Cultural_Context explains the
metaphor. Using the short translation as the gold standard loses the cultural
richness. A model that knows English proverbs might recognize "like a shadow"
as "shadow" = "follows closely" without understanding the Arabic cultural
context.

Reviewer question: For Arabic, does the benchmark test:
(a) Recognition of English proverb equivalents?
(b) Understanding of Arabic cultural metaphors?

The current design tests (a), but the data supports (b).

---

CRITICAL FLAW #3: ENGLISH "CORRECT_MEANING" IS NOT A TRANSLATION
------------------------------------------------------------------

English proverbs don't NEED translation — they're already in English. The
`Correct_Meaning` column contains EXPLANATIONS:

  Proverb: "A bird in the hand is worth two in the bush"
  Meaning: "The proverb means that it's better to hold onto something you
            have rather than take the risk of getting something better..."

The S2 generator was asked to produce "a correct paraphrase of the English
translation." But there IS no English translation — the proverb IS English.
The generator was paraphrasing an EXPLANATION while being told it was a
TRANSLATION. This explains the 21.3% fallback: the task is ill-defined.

For English, a meaningful benchmark would ask: "Given this proverb, which
explanation best captures its meaning?" — but that requires the explanation
to be the gold standard, not a paraphrase target.

---

CRITICAL FLAW #4: PROVENANCE METADATA IS UNUSED
------------------------------------------------

Yoruba has `Provenance` (source document: part1.docx through part7.docx) and
`Comments` (annotator notes about errors). These are quality signals.

The pipeline ignored them. A benchmark that ignores provenance and annotator
comments is not rigorous. The Comments reveal systematic issues:
- "Fix space in the target_text_en"
- "Removed hyphen... it was absent in the original"
- "old way of writing it"

These are not cosmetic. They indicate that the Target_Text_En may not match
the Source_Text_Yo in some items.

---

CRITICAL FLAW #5: NO CULTURAL CONSULTANT INVOLVEMENT
-----------------------------------------------------

For low-resource figurative language, cultural validity requires community
involvement. The paper has no acknowledgments of Yoruba or Arabic cultural
consultants, no community review, no native speaker validation of distractors.

The 36% Yoruba S2 fallback is attributed to "qwen3-32b struggles with
low-resource figurative language." But perhaps qwen3 fails because the task
is ill-specified: it's asked to paraphrase a translation when it should be
asked to generate culturally plausible distractors for a meaning.

---

POSITIVE ASPECTS
----------------
1. The dataset is large (3,974 Yoruba, 913 Arabic, 2,278 English).
2. The Cultural_Context column is a genuine asset — most proverb benchmarks
   lack this.
3. The QA_Flag system shows data curation effort.
4. The cross-family generator design is methodologically sound.

---

OVERALL RECOMMENDATION: REJECT (major revision)
------------------------------------------------

The benchmark has a cultural validity crisis. The data supports a rich,
meaning-based evaluation, but the pipeline implements a shallow,
translation-based one. Before resubmission:

1. Redesign the task as "proverb meaning comprehension" for all languages
2. Use Cultural_Context (or Correct_Meaning) as the gold standard
3. Involve native speakers in distractor validation
4. Filter by QA_Flag and address Comments
5. Report separate scores for translation vs. meaning tasks if both are kept
6. Acknowledge provenance and annotation limitations

Estimated revision time: 6–8 weeks (requires human annotation/validation).



======================================================================
SOURCE: phase3_reviewer_stats.txt
======================================================================

================================================================================
PHASE 3A: EMNLP/ACL REVIEWER #3 — STATISTICAL RIGOR & EXPERIMENTAL DESIGN
================================================================================

Reviewer Profile: EMNLP reviewer with statistics background, focus on
experimental design, significance testing, and benchmark validity. Has
published on MMLU-Pro, HellaSwag, and critique of LLM evaluation practices.

---

CRITICAL FLAW #1: MCNEMAR TEST IS INAPPROPRIATE
-----------------------------------------------

The paper reports McNemar's test (p < 0.001) comparing S1 (86.8%) vs. S2
(62.5%). But McNemar requires paired observations — the same items evaluated
by the same models under both strategies. The paper does NOT clarify whether
this condition is met.

Questions:
- Are the 150 S1 items the SAME 150 proverbs as the 150 S2 items?
- Are the 3,600 S2 evaluations (150 items × 2 models × 3 styles × ...)
  directly comparable to the S1 evaluations?
- If S1 and S2 have different fallback rates (0% vs. 21.3%), the denominators
differ. McNemar assumes the same N for both conditions.

If fallback items are excluded from S2 accuracy but included in S1, the
denominators are different and McNemar is invalid.

---

CRITICAL FLAW #2: FALLBACK ITEMS INFLATE THE DENOMINATOR
---------------------------------------------------------

S2 has 21.3% fallback = ~32 of 150 items have placeholder distractors.
These items are trivially answerable. Including them in the 62.5% calculation
inflates the apparent accuracy.

Correct approach: Report accuracy on:
(a) ALL items (including fallback) — shows pipeline reliability
(b) NON-FALLBACK items only — shows true distractor hardness
(c) FALLBACK items separately — shows pipeline failure rate

The paper reports only (a), which conflates pipeline reliability with
distractor quality.

---

CRITICAL FLAW #3: BOOTSTRAP CI WITHOUT STRATIFICATION
------------------------------------------------------

The paper reports bootstrap CI [58.1%, 66.6%] for S2 accuracy. But if the
sample includes 21% fallback items (which have ~100% accuracy because they're
trivial), the bootstrap is mixing two distributions:
- Distribution A: Fallback items → ~100% accuracy
- Distribution B: Genuine S2 items → ~50% accuracy (estimated)

The CI is not interpretable without stratifying by fallback status.

---

CRITICAL FLAW #4: N=150 IS UNDERPOWERED FOR CROSS-LINGUAL CLAIMS
------------------------------------------------------------------

50 items per language × 2 strategies × 2 models × 3 styles = 600 evaluations
per language. With 50 items, the standard error of a proportion is:
  SE = sqrt(p(1-p)/50) ≈ sqrt(0.625×0.375/50) ≈ 0.069 = 6.9%

A 6.9% margin of error means the observed 62.5% could be 55.6%–69.4%.
Cross-lingual comparisons (English 71.3% vs. Yoruba 46.2%) have overlapping
CIs and may not be statistically significant.

The paper's claim that "English shows the strongest performance" may not
survive proper significance testing with Bonferroni correction for multiple
comparisons.

---

CRITICAL FLAW #5: NO BASELINE COMPARISON TO HUMAN PERFORMANCE
--------------------------------------------------------------

A benchmark without human performance is uninterpretable. If humans score 95%
on S1 and 90% on S2, then model scores of 86.8%/62.5% are concerning. If
humans score 70%/40%, the models are actually doing well.

The paper has no human baseline. This is standard practice (MMLU, HellaSwag)
but for a NEW benchmark in a niche domain (proverb understanding), human
performance is essential for calibration.

---

CRITICAL FLAW #6: COMMITTEE SIZE OF 2 IS TOO SMALL
--------------------------------------------------

The committee has 2 models: llama-4-maverick and allam-2-7b.
With 2 models, "unanimous consensus" is not a strong signal — it's just
both models agreeing. A 2-model committee cannot detect idiosyncratic
failures.

The paper dropped llama-3.3-70b due to API failures, but this means the
committee was selected based on API availability, not methodological criteria.
This introduces selection bias: the committee consists of models that happen
to work, not models chosen for coverage or diversity.

---

POSITIVE ASPECTS
----------------
1. The use of McNemar (even if potentially misapplied) shows awareness of
   paired-test requirements.
2. Bootstrap CI is appropriate in principle.
3. The 24.3 pp gap between S1 and S2 is large enough to be interesting even
   with wide CIs.

---

OVERALL RECOMMENDATION: REJECT (major revision)
------------------------------------------------

The statistical analysis needs fundamental restructuring:
1. Clarify whether McNemar assumptions are met (same items, same models)
2. Stratify all analyses by fallback status
3. Add human baseline (30 items minimum)
4. Report per-language significance with Bonferroni correction
5. Justify the 2-model committee or expand it
6. Increase N to at least 100 per language for cross-lingual claims

Estimated revision time: 4–6 weeks.



======================================================================
SOURCE: phase3_reviewer_repro.txt
======================================================================

================================================================================
PHASE 3B: ACL/NAACL REVIEWER #4 — REPRODUCIBILITY & ETHICS CRITIQUE
================================================================================

Reviewer Profile: ACL reviewer focusing on reproducibility, dataset ethics,
and responsible AI. Has reviewed HELM, BIG-bench, and cultural NLP datasets.
Chaired the reproducibility track at EMNLP 2024.

---

CRITICAL FLAW #1: API KEYS ARE HARDCODED IN SOURCE CODE
--------------------------------------------------------

The codebase contains hardcoded API keys in the source file:
  `proverbgap_kaggle_final.py`

This is a reproducibility AND security issue:
- Other researchers cannot run the code without their own keys
- The keys in the published code may be revoked, making reproduction impossible
- Hardcoded keys in version control are a security vulnerability

Standard practice: Use environment variables or a config file that is
.gitignored. The paper does not mention how others should obtain API access.

---

CRITICAL FLAW #2: NO RANDOM SEED REPORTING FOR GENERATION
----------------------------------------------------------

The S2 generator uses `seed=GEN_SEED + attempt` where GEN_SEED = 42. But
temperature = 0.7 means the seed may not fully determine output. The paper
does not report:
- Whether seeds are deterministic across API providers
- Whether different runs with the same seed produce identical outputs
- The variance across multiple generation runs

For reproducibility, the paper should report generation variance: run S2
3 times with different seeds and report accuracy ranges.

---

CRITICAL FLAW #3: CACHE INVALIDATION IS NOT DOCUMENTED
-------------------------------------------------------

The pipeline uses an SQLite cache (`.api_cache.sqlite`). If a cached response
is corrupted or stale, reproduction will fail silently. The paper does not:
- Document cache invalidation criteria
- Provide a flag to disable caching
- Report cache hit rates

---

CRITICAL FLAW #4: NO DATASET CARD FOR actual_data
--------------------------------------------------

The repository has `DATASET_CARD.md` but it describes the WRONG data
(original_data). The actual_data — with Cultural_Context, QA_Flag,
Provenance — has no dataset card.

A proper dataset card should include:
- Annotation protocol (who annotated, how, inter-annotator agreement)
- QA_Flag definitions (what does FIX mean? Who applied it?)
- Provenance documentation (what are part1.docx–part7.docx?)
- Cultural consultant involvement
- License and usage restrictions

---

CRITICAL FLAW #5: NO ETHICS STATEMENT FOR CULTURAL DATA
--------------------------------------------------------

Yoruba and Arabic proverbs are cultural heritage. Using them in a benchmark
without:
- Community consent or consultation
- Attribution to cultural sources
- Plans for community benefit

raises ethical concerns. The paper's "Future Work" section mentions human
evaluation but not community involvement.

The Provenance column (part1.docx–part7.docx) suggests the data was extracted
from documents. Were these documents published with permission? Are the
proverb collectors acknowledged?

---

CRITICAL FLAW #6: BUDGET DISCLOSURE IS INAPPROPRIATE
-----------------------------------------------------

The paper mentions a "$50 budget" for API costs in the review document.
This is unprofessional for an academic paper. Benchmark papers should report:
- Total compute cost in dollars or GPU-hours
- API provider costs per model
- Not frame it as a personal expense budget

---

POSITIVE ASPECTS
----------------
1. The code is well-structured and self-contained.
2. The checkpointing system is good for long runs.
3. The contamination filter shows awareness of data leakage.
4. The Git history (if published) provides provenance for code changes.

---

OVERALL RECOMMENDATION: REJECT (major revision)
------------------------------------------------

Before resubmission:
1. Remove all hardcoded keys; document API requirements
2. Add dataset card for actual_data with annotation details
3. Report generation variance across seeds
4. Add ethics statement for cultural data usage
5. Remove budget language; report costs professionally
6. Document cache behavior and provide disable flag

Estimated revision time: 2–3 weeks.



======================================================================
SOURCE: phase4_researcher_deepmind.txt
======================================================================

================================================================================
PHASE 4A: GOOGLE DEEPMIND / META AI RESEARCHER — TECHNICAL SALVAGE PLAN
================================================================================

Researcher Profile: Senior researcher at a top AI lab, 10+ years in
benchmark design, low-resource NLP, and LLM evaluation. Has built MMLU,
BIG-bench, and culturally situated evaluation frameworks. Focused on
practical, implementable solutions.

---

SITUATION ASSESSMENT: SEVERE BUT SALVAGEABLE
----------------------------------------------

The data-model mismatch is severe but not fatal. The actual_data has RICHER
information than the pipeline was designed for. The problem is that the
pipeline used the WRONG column, not that the data is bad.

Key assets:
- English: 2,278 proverbs with Correct_Meaning (explanations)
- Arabic: 913 proverbs with translation + Cultural_Context
- Yoruba: 3,974 proverbs with translation + Cultural_Context + QA_Flag

These are high-quality, curated datasets. The mistake was in the pipeline's
assumptions, not the data itself.

---

SALVAGE STRATEGY: MINIMAL REWORK PATH (2 WEEKS)
------------------------------------------------

The fastest path to a valid benchmark is to reframe the task and update the
pipeline to use the correct columns.

STEP 1: REDEFINE THE TASK (Day 1)
----------------------------------
Change from "translation comprehension" to "proverb meaning comprehension."

For each language:
- English: Gold standard = `Correct_Meaning` (explanation)
- Arabic: Gold standard = `Cultural_Context` (cultural explanation)
- Yoruba: Gold standard = `Cultural_Context` (cultural explanation)

The task becomes: "Given a proverb in [language], which explanation best
captures its cultural meaning?"

This is MORE interesting than translation matching because:
- It tests deeper comprehension
- It avoids the "English proverb recognition" shortcut
- It aligns with the actual data

STEP 2: UPDATE COLUMN MAPPING (Day 1)
--------------------------------------
In `proverbgap_kaggle_final.py`, change the column map:

  English: 'Correct_Meaning' → 'proverb_en' (now it's the gold meaning)
  Arabic:  'Cultural_Context' → 'proverb_en' (ignore translation column)
  Yoruba:  'Cultural_Context' → 'proverb_en' (ignore translation column)

This is a 3-line change.

STEP 3: UPDATE S2 GENERATOR PROMPT (Day 2)
-------------------------------------------
Current prompt:
  "Correct English translation: {translation}\nGenerate 4 options..."

New prompt:
  "Proverb: {proverb}\nCultural meaning: {meaning}\n\nGenerate 4 explanations
  in a valid JSON list of strings. Option 1 must be a correct paraphrase of
  the cultural meaning. Options 2-4 must be incorrect explanations with
  subtle meaning shifts."

This is a prompt change, not a code change.

STEP 4: FILTER YORUBA BY QA_FLAG (Day 2)
-----------------------------------------
Exclude rows where QA_Flag == 'DROP'.
Review rows where QA_Flag == 'FIX' — manually decide inclusion.
Include rows where QA_Flag == 'PERFECT' or NULL.

This reduces Yoruba from 3,974 to ~3,935 (removing 39 DROP items).

STEP 5: UPDATE EVALUATION PROMPT (Day 3)
-----------------------------------------
Change from:
  "What is the correct meaning/translation?"

To:
  "What is the correct explanation of this proverb's cultural meaning?"

STEP 6: RERUN PILOT (Days 4–7)
-------------------------------
Run N=50 per language with the corrected pipeline.
This validates that the fix works end-to-end.

STEP 7: SCALE TO N=700 (Week 2)
--------------------------------
If pilot succeeds, scale to N=700 per language.

---

ALTERNATIVE: TWO-TASK BENCHMARK (4 WEEKS)
------------------------------------------

If the authors want to preserve translation matching AND add meaning
comprehension, they can build a two-task benchmark:

Task A (Translation): Match proverb to english_translation
Task B (Meaning): Match proverb to Cultural_Context / Correct_Meaning

This is more work but more comprehensive:
- Requires generating two sets of distractors per proverb
- Requires double the API calls
- Requires separate analysis and reporting

Verdict: Do Task B only (meaning) for the initial submission. Add Task A
as future work.

---

TECHNICAL RISK ASSESSMENT
--------------------------
Risk 1: S2 generator may struggle with meaning paraphrasing
  - Mitigation: The semantic gate (Jaccard ≥ 0.25) already checks meaning
    similarity. May need to tune threshold.

Risk 2: Meaning explanations are longer than translations
  - Mitigation: Increase length threshold from 0.35 to 0.50.

Risk 3: Arabic Cultural_Context is much longer than translation
  - Mitigation: Generator has 512 tokens — sufficient for 153-char contexts.

Risk 4: English Correct_Meaning contains proverb text in 3.3% of cases
  - Mitigation: Add a filter to reject options that contain the proverb text.

---

RECOMMENDATION
---------------
Proceed with the Minimal Rework Path. The data is good. The pipeline is
mostly correct. The fix is a column mapping change + prompt rewrite. Do NOT
rebuild from scratch.

Estimated time to valid pilot: 1 week.
Estimated time to N=700: 2–3 weeks.



======================================================================
SOURCE: phase4_researcher_openai.txt
======================================================================

================================================================================
PHASE 4B: OPENAI / ANTHROPIC RESEARCHER — STRATEGIC PUBLICATION PLAN
================================================================================

Researcher Profile: Research lead at a frontier AI lab, focus on evaluation
methodology, benchmark design, and publication strategy. Has shepherded
multiple benchmarks from idea to NeurIPS/ICML. Advisor to 5+ PhD students.

---

STRATEGIC ASSESSMENT: PUBLISHABLE, BUT NOT AS-IS
-------------------------------------------------

The current paper has a fatal flaw (data-model mismatch) but the underlying
contribution is strong. The question is not WHETHER to publish, but WHAT to
publish and WHEN.

Three options:

OPTION A: Fix Everything, Submit to ACL/EMNLP 2026 (6–8 weeks)
OPTION B: Publish a Dataset Paper Now, Full Benchmark Later (2–3 weeks)
OPTION C: Workshop Paper at CoNNL/Eval4NLP 2025, Full Paper Later (4 weeks)

---

OPTION A: FULL PAPER (ACL/EMNLP 2026)
--------------------------------------

Pros:
- Highest impact venue
- Full benchmark with N=700
- Complete analysis

Cons:
- 6–8 weeks of work
- High rejection risk if not perfectly executed
- Competitive venue

Requirements:
1. Fix data-model mismatch (1 week)
2. Rerun pilot + scale to N=700 (2 weeks)
3. Human validation (2 weeks)
4. Rewrite paper (2 weeks)
5. Response to all reviewer critiques (1 week)

Verdict: Viable if the team has 2 months. High risk, high reward.

---

OPTION B: DATASET PAPER (LREC, EACL, or arXiv) — RECOMMENDED
-------------------------------------------------------------

Pros:
- Fastest path to publication
- Dataset papers have lower bar for acceptance
- Establishes priority on the dataset
- Can cite the dataset paper in the full benchmark paper later

Content:
- Describe the actual_data: 3 languages, 7,165 proverbs, rich annotations
- Document collection, cleaning, QA process
- Present the column structure and annotation protocol
- Release the data with proper license
- Include a small pilot (N=50) as proof-of-concept
- Do NOT make strong benchmark claims

Venue options:
- LREC-COLING 2026 (dataset track)
- EACL 2026 (resource paper)
- arXiv preprint + EMNLP Findings 2026

Timeline: 2–3 weeks.

---

OPTION C: WORKSHOP PAPER (CoNNL/Eval4NLP 2025)
-----------------------------------------------

Pros:
- Fast feedback from community
- Lower bar for acceptance
- Can present the negative results as a case study

Content:
- "Lessons from Building a Cross-Lingual Proverb Benchmark: A Negative Results
   Study"
- Document the data-model mismatch
- Present the pipeline hardening as a methodology contribution
- The 21.3% fallback rate is a genuine finding about LLM distractor generation
- The API infrastructure collapse (v4.3.3) is a cautionary tale

This reframes the mistake as a contribution: "Here's what we learned about
building robust LLM evaluation pipelines."

Timeline: 4 weeks.

---

MY RECOMMENDATION: HYBRID APPROACH
-----------------------------------

1. IMMEDIATELY (this week):
   - Write a dataset description paper for arXiv
   - Release the actual_data with a proper dataset card
   - This establishes priority and gets community feedback

2. SHORT-TERM (next 2–3 weeks):
   - Fix the pipeline (Minimal Rework Path from Researcher A)
   - Run corrected pilot (N=50 per language)
   - Write a workshop paper (CoNNL/Eval4NLP 2025) on the methodology

3. MEDIUM-TERM (2–3 months):
   - Scale to N=700
   - Add human validation
   - Submit full benchmark paper to ACL/EMNLP 2026

This gives the team THREE publications from one project:
- Dataset paper (arXiv/LREC)
- Methodology paper (workshop)
- Full benchmark paper (ACL/EMNLP)

---

WHAT TO TELL BUSAYOU
---------------------

The user mentioned "Busayou" — likely the supervisor or collaborator.

Message:
"We discovered that the pipeline was using simplified data instead of the
rich annotated data. The good news: the actual data is BETTER than what we
thought we had. It supports a more interesting benchmark (meaning comprehension
instead of translation matching). The fix is 1 week of work. We have three
publication options ranging from 2 weeks to 3 months. I recommend the hybrid
approach: dataset paper now, full benchmark later."

---

FINAL VERDICT
--------------
Do NOT abandon the project. The data is the project's strongest asset. The
mistake is fixable. The timeline is recoverable. Publish in phases.



======================================================================
PHASE 5: EXECUTIVE SYNTHESIS — WHAT TO DO NEXT
======================================================================


## THE MISTAKE

The pipeline used `original_data/` (Proverb + Translation) when it should have
used `actual_data/` (rich annotations including Cultural_Context, Correct_Meaning,
QA_Flag, Provenance, Comments).

| Language | Used (WRONG) | Should Use (CORRECT) |
|----------|-------------|----------------------|
| English  | Translation | `Correct_Meaning` (explanation) |
| Arabic   | Translation | `Cultural_Context` (cultural meaning) |
| Yoruba   | Translation | `Cultural_Context` (cultural meaning) |

This means the ENTIRE benchmark task was wrong. We tested "match proverb to
translation" when the data supports "match proverb to cultural meaning."

## THE GOOD NEWS

1. The actual data is RICHER and BETTER than what we used
2. The pipeline code is mostly correct — just pointed at wrong columns
3. The fix is ~1 week of work (column remap + prompt rewrite)
4. The data supports a MORE INTERESTING benchmark (meaning comprehension)

## CONSENSUS FROM ALL 8 AGENTS

ALL reviewers agree:
- The paper is NOT reviewable as-is (reject/major revision)
- The data-model mismatch is the fatal flaw
- The data itself is high-quality and valuable
- The project is salvageable

## RECOMMENDED PATH FORWARD (HYBRID APPROACH)

### Week 1: Emergency Fix
1. Change column mapping in `proverbgap_kaggle_final.py`
   - English: `Correct_Meaning` → gold standard
   - Arabic: `Cultural_Context` → gold standard
   - Yoruba: `Cultural_Context` → gold standard
2. Rewrite S2 generator prompt for "cultural meaning" not "translation"
3. Filter Yoruba: exclude QA_Flag == 'DROP', review 'FIX'
4. Update evaluation prompt to ask about "meaning" not "translation"
5. Rerun N=50 pilot

### Week 2–3: Dataset Paper (arXiv)
- Write dataset description paper
- Release actual_data with proper dataset card
- Establish priority on the rich annotated dataset
- Cite: 7,165 proverbs, 3 languages, meaning annotations

### Month 2–3: Full Benchmark Paper (ACL/EMNLP 2026)
- Scale to N=700 with corrected pipeline
- Add human validation (30 items per language)
- Add position bias ablation
- Report stratified accuracy (with/without fallback)
- Add ethics statement and cultural consultant acknowledgments

### Parallel: Methodology Workshop Paper
- "Lessons from Building Cross-Lingual Proverb Benchmarks"
- Negative results: API fragility, fallback rates, same-family exploitation
- Submission to CoNNL/Eval4NLP 2025

## FILES CHANGED

- `proverbgap_kaggle_final.py` — column mapping + prompts
- `proverbgap_kaggle_final.ipynb` — regenerated
- `DATASET_CARD.md` — rewrite for actual_data
- Paper draft — reframe as "meaning comprehension"

## WHAT TO TELL BUSAYOU

"We found the real data. It's better than what we used. The benchmark should
test 'proverb meaning comprehension' not 'translation matching.' The fix is
1 week. We can publish a dataset paper in 2–3 weeks and a full benchmark in
2–3 months. The project is stronger now, not weaker."
