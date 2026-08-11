# ProverbGap MCQ Human Annotation Protocol

## Purpose and Scope

This protocol defines the human annotation workflow for validating Multiple-Choice Questions (MCQs) generated from the ProverbGap dataset. The goal is to assess annotation quality, measure inter-annotator agreement (IAA), and verify that the generative pipeline produces shortcut-resistant distractors.

**Languages:** English, Arabic, Yoruba  
**Task:** Blind options-only annotation for cross-lingual proverb understanding

## Annotator Requirements

### Primary Qualifications

1. **Native speakers** preferred for each target language:
   - English: Native or C2 proficiency
   - Arabic: Native or C1+ proficiency (Modern Standard Arabic or any dialect)
   - Yoruba: Native or near-native fluency

2. **Secondary qualifications:**
   - Completed secondary education in the target language culture
   - Familiarity with proverbial expressions in the target language
   - No prior exposure to the ProverbGap dataset or this annotation task

3. **Recruitment target:** 3 annotators per language (total 9), with minimum 2 required for IAA computation

## Task Description

Each annotation item presents:
1. A proverb in its original language
2. Four English options labeled A, B, C, D

### Annotation Instructions

For each item, annotators must provide:

1. **Correct Answer** (required): Select the letter (A, B, C, or D) that best captures the proverb's meaning.

2. **Distractor Plausibility Ratings** (required): Rate how plausible each option would be as a distractor on a 5-point scale:
   - 1: Clearly wrong / nonsensical
   - 2: Weak but possible
   - 3: Moderately plausible
   - 4: Very plausible
   - 5: Could be correct / highly tempting

3. **Shortcut Flags** (optional per item, at least one required per batch):
   - `same_structure`: Distractor has same grammatical structure as correct answer
   - `length_outlier`: Distractor is clearly longer/shorter than others
   - `semantic_echo`: Distractor repeats words from the proverb
   - `generic_idiom`: Distractor is a generic English idiom
   - `cultural_mismatch`: Distractor mismatches cultural context
   - `none`: No obvious shortcuts detected

4. **Confidence Rating** (required): Self-rated confidence in answer:
   - 1: Low confidence (guessing)
   - 2: Medium confidence (some uncertainty)
   - 3: High confidence (certain)

## Rubric Definition

### Plausibility Scale

| Score | Criteria |
|-------|----------|
| 1 | Wrong answer detectable without cultural knowledge; obviously unrelated |
| 2 | Wrong answer but shows partial understanding of semantic domain |
| 3 | Compelling for someone partially familiar with the culture |
| 4 | Would fool most non-experts; subtle misdirection |
| 5 | Indistinguishable from correct answer; expert-level confusion |

### Shortcut Flag Guide

- **same_structure**: Same agent, action, or grammatical frame
- **length_outlier**: >50% length difference from median
- **semantic_echo**: Shares key terms/structure with proverb text
- **generic_idiom**: Recognizable idiom not specific to culture
- **cultural_mismatch**: Applies cultural concept incorrectly
- **none**: No shortcuts detected

## Blinding Procedure

1. All items are presented without correct answer revealed
2. Options are randomized per annotator using deterministic seed
3. Validation ID is a hash linking to master data (not revealed to annotators)
4. All vote columns, consensus labels, and correct_meaning columns removed from annotation view
5. Annotators see only: `validation_id`, `language`, `proverb`, `option_A`, `option_B`, `option_C`, `option_D`, and empty annotation fields

## Quality Controls

### Attention Checks

- Embedded "trap" items where correct answer is obviously wrong
- Items with repeated proverbs across annotators for consistency check
- Minimum accuracy threshold: 80% on trap items

### Timing Constraints

- Minimum time per item: 10 seconds (enforced by interface)
- Maximum time per item: 120 seconds (flags potential inattention)
- Session breaks recommended every 30 items

### Data Validation

- Required fields validated on submission
- Plausibility ratings checked for monotonic ordering
- Consistency checks for repeated proverbs

## Data Handling and Privacy

1. **Data retention:** Raw annotations stored in encrypted CSV, access restricted to research team
2. **Anonymization:** Annotator IDs hashed; no personally identifying information collected
3. **Consent:** Email consent required before assignment
4. **Compensation:** [To be determined based on institution policies]
5. **IRB:** Protocol submitted to [institution] IRB under exemption category [to be determined]

## IAA Computation Plan

### Primary Metric

**Fleiss' Kappa** for categorical agreement on correct answers across annotators.

### Secondary Metrics

1. **Per-language Kappa** for language-specific analysis
2. **Item-level agreement** for identifying ambiguous items
3. **Plausibility rating correlation** (Pearson/Spearman) across annotators

### Sample Size for IAA

Based on Flack et al. / Rotondi & Donner formulas, targeting kappa ≥ 0.6 with 80% power requires approximately 30 items per language. With 3 annotators per language and 90 total items, we achieve adequate power to detect meaningful agreement.

### Agreement Quality Thresholds

| Kappa | Interpretation | Action |
|-------|----------------|--------|
| < 0.4 | Poor | Investigate systematic errors |
| 0.4 - 0.6 | Fair | Acceptable for exploratory |
| 0.6 - 0.8 | Good | Publishable quality |
| > 0.8 | Excellent | Gold standard potential |