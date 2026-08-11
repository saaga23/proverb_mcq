# v66 Kaggle Run — Detailed Analysis

- Run timestamp: 2026-06-21T15:59:05.845412+00:00
- Notebook version: 66
- N_PER_LANG: 1
- Cost: $0.1754 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash']
- Benched generators: []
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']
- Total MCQs: 36 (3 langs x 3 gens x 4 variants)

## Quality-gate evolution

| Gate | v58 | v59 | v60 | v61 | v66 | Target |
|---|---|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.23 | $0.1864 | $0.1754 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | 47.2% | 55.6% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | 25.0% | 22.2% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | 47.2% | 50.0% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | 61.1% | 69.4% | — |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | 33.3% | 50.0% | ≥50% |

## Per-language consensus correctness

- Arabic: 58.3% (n=12)  — mean consensus frac 0.83
- English: 100.0% (n=12)  — mean consensus frac 0.96
- Yoruba: 50.0% (n=12)  — mean consensus frac 0.77

## Generation status breakdown

generation_status
generated          18
partial            16
length_fallback     2
Name: count, dtype: int64

### By generator

generation_status        generated  length_fallback  partial
generator_model                                             
google/gemini-2.5-flash          6                0        6
google/gemma-4-31b-it            7                1        4
qwen/qwen3.7-max                 5                1        6

### By variant

generation_status          generated  length_fallback  partial
variant                                                       
adversarial-hard-negative          2                1        6
adversarial-length-locked          4                1        4
overgenerate-select                7                0        2
taxonomy-guided                    5                0        4

### By language

generation_status  generated  length_fallback  partial
language                                              
Arabic                     5                0        7
English                    8                0        4
Yoruba                     5                2        5

## Fallback-count diagnostics

- Mean fallback_count: 0.78
- Mean length_replaced: 0.03
- Mean leak_replaced: 0.17
- Mean nli_replaced: 0.44

## Per-variant consensus accuracy (language=ALL)

        generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
       qwen/qwen3.7-max adversarial-length-locked  3            0.666667             0.916667   FAIL
       qwen/qwen3.7-max adversarial-hard-negative  3            1.000000             0.833333   FAIL
       qwen/qwen3.7-max           taxonomy-guided  3            1.000000             0.916667   FAIL
       qwen/qwen3.7-max       overgenerate-select  3            1.000000             0.916667   FAIL
  google/gemma-4-31b-it adversarial-length-locked  3            1.000000             0.833333   FAIL
  google/gemma-4-31b-it adversarial-hard-negative  3            0.666667             0.833333   FAIL
  google/gemma-4-31b-it           taxonomy-guided  3            0.666667             0.750000   FAIL
  google/gemma-4-31b-it       overgenerate-select  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash adversarial-length-locked  3            0.666667             1.000000   FAIL
google/gemini-2.5-flash adversarial-hard-negative  3            0.333333             0.750000 REVIEW
google/gemini-2.5-flash           taxonomy-guided  3            0.333333             0.916667 REVIEW
google/gemini-2.5-flash       overgenerate-select  3            0.333333             0.750000 REVIEW

## Length-fallback deep dive

Total length_fallback items: 2 / 36 (5.6%)

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=113, B=84, C=134, D=132 (median=122)
  - A. (113 chars, 0.92x median) The pericarp of the palm fruit that is wedged atop the palm tree is a burden that the palm tree itself must bear.
  - B. (84 chars, 0.69x median) One is never so fortunate at daily thievery that it matches owning one’s own things.
  - C. (134 chars, 1.09x median) A uniquely flawed individual will ultimately instruct the community on the precise method needed to carry their specific daily burden.
  - D. (132 chars, 1.08x median) The place where the water is clear is not deep enough for the gourd; the place where the water is deep enough, though, is dangerous.

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=58, B=59, C=55, D=48 (median=56)
  - A. (58 chars, 1.03x median) A flawed object forces the creator to improve their skill.
  - B. (59 chars, 1.04x median) Money is the elder sibling; a child is the younger sibling.
  - C. (55 chars, 0.97x median) A neckless gourd proves the farmer's method was flawed.
  - D. (48 chars, 0.85x median) When a duty is one’s turn, one does not duck it.

## Partial items deep dive

Total partial items: 16 / 36

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. An individual should support their own household before donating resources to the public.
  - B. Don't sell the skin before you've caught the bear.
  - C. A family should keep their valuable possessions hidden before displaying them to the public.
  - D. A homeowner must forbid strangers from entering before allowing them into the sanctuary.

### google_gemini-2.5-flash_adversarial-length-locked_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. The stupid might want to help you, but they just ended up hurting you.
  - B. It is essential to prioritize community needs over individual family concerns for the greater good.
  - C. One's primary responsibility is to provide for their immediate household before extending assistance elsewhere.
  - D. Financial resources should always be directed towards religious institutions before personal expenses.

### qwen_qwen3.7-max_adversarial-length-locked_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Critics should examine their own flaws first.
  - B. Enduring bitter betrayals gradually hardens our emotional defenses and cynicism.
  - C. Overcoming financial disasters ultimately builds our material wealth and prosperity.
  - D. Enduring severe hardships ultimately builds our inner resilience and fortitude.

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A challenging situation will reveal the best way to handle it.
  - B. Sedately is the way an elderly masquerader dances.
  - C. One must always adapt to the tools available for a task.
  - D. Difficult tasks require the guidance of an experienced elder.

### google_gemma-4-31b-it_adversarial-hard-negative_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Don't poke your nose into others' affairs.
  - B. Ensure your home is luxurious before donating to the needy.
  - C. Prioritize the needs of your own family before helping others.
  - D. Your sins have caught up with you

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Climbing the ladder of success by stepping on others.
  - B. While you want to build, others want to tear down.
  - C. The apple doesn't fall far from the tree.
  - D. One should prioritize their family's needs before assisting others.

### qwen_qwen3.7-max_adversarial-hard-negative_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Surviving severe difficulties ultimately builds our resilience and inner strength.
  - B. Enduring severe difficulties primarily teaches us to avoid future risks and dangers.
  - C. If something is working fine, don't interfere.
  - D. You cannot change something that has already happened.

### google_gemma-4-31b-it_adversarial-hard-negative_English_1
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Surviving a crisis ensures that we will never suffer again.
  - B. Facing hardships helps us become more resilient and capable.
  - C. Fear makes you do things faster than would normally seem possible.
  - D. Overcoming a trauma removes the possibility of future pain.

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The person on whose arrival one advances against the enemy: he says all he will do is blow the bugle.
  - B. Compatibility of character means compat ibility in friendship.
  - C. A person lacking proper family roots will naturally require the community to dictate how they should behave.
  - D. A person with an unusual character will naturally reveal the specific method required to manage them properly.

### google_gemini-2.5-flash_adversarial-hard-negative_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A difficult task requires a strong leader to guide the community.
  - B. A challenging situation will reveal the best way to handle it.
  - C. The reach of the tongue is never as far as the nose.
  - D. The community must come together to solve an unexpected dilemma.

### qwen_qwen3.7-max_taxonomy-guided_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Don't sell the skin before you've caught the bear.
  - B. People must fund local civic projects before giving to distant religious organizations.
  - C. One must provide for their own household before offering charity to the wider community.
  - D. Domestic necessities are strictly forbidden from ever being kept inside places of worship.

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Put your money where your mouth is.
  - B. Give generously to the community to ensure blessings
  - C. Offer help to the public regardless of home needs
  - D. Prioritize your own family's needs before helping others

### qwen_qwen3.7-max_taxonomy-guided_English_1
- Generator: qwen/qwen3.7-max | Variant: taxonomy-guided | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Enduring severe adversity primarily guarantees our continued physical survival through painful times.
  - B. Surviving severe adversity ultimately builds greater psychological resilience and personal fortitude.
  - C. Surviving lethal physical threats allows the human body to develop robust biological immune responses.
  - D. Beware of an offer or opportunity that sounds too good to be true.

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Money that does not exist, no king can take from you.
  - B. One must adapt their methods when faced with an unusual problem.
  - C. A challenging situation will reveal the true skill of an individual.
  - D. Even a flawed vessel can serve a useful purpose if handled with care.

### google_gemini-2.5-flash_overgenerate-select_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. He who fears the wolf does not herd sheep
  - B. One should prioritize their household's needs before assisting the community.
  - C. It is better to give to the needy than to hoard wealth for oneself.
  - D. Religious institutions should not interfere with family matters.

### google_gemma-4-31b-it_overgenerate-select_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A leopard that struts is not answered by strutting from a dog.
  - B. The broken gourd proves that the harvest was too heavy.
  - C. A flawed vessel teaches the craftsman how to fix it.
  - D. A neckless gourd shows that the planter lacked foresight.

## Parse-fallback reasons

Total parse_fallback rows: 0


## High-consensus-wrong items

Count: 8 / 36 (22.2%)

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The pericarp of the palm fruit that is wedged atop the palm tree is a burden that the palm tree itself must bear.
  - B. One is never so fortunate at daily thievery that it matches owning one’s own things.
  - C. A uniquely flawed individual will ultimately instruct the community on the precise method needed to carry their specific daily burden.
  - D. The place where the water is clear is not deep enough for the gourd; the place where the water is deep enough, though, is dangerous.
- Correct label: C | Consensus: D (frac=1.00)

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A challenging situation will reveal the best way to handle it.
  - B. Sedately is the way an elderly masquerader dances.
  - C. One must always adapt to the tools available for a task.
  - D. Difficult tasks require the guidance of an experienced elder.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemma-4-31b-it_adversarial-hard-negative_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Don't poke your nose into others' affairs.
  - B. Ensure your home is luxurious before donating to the needy.
  - C. Prioritize the needs of your own family before helping others.
  - D. Your sins have caught up with you
- Correct label: C | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Climbing the ladder of success by stepping on others.
  - B. While you want to build, others want to tear down.
  - C. The apple doesn't fall far from the tree.
  - D. One should prioritize their family's needs before assisting others.
- Correct label: D | Consensus: C (frac=0.75)

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Put your money where your mouth is.
  - B. Give generously to the community to ensure blessings
  - C. Offer help to the public regardless of home needs
  - D. Prioritize your own family's needs before helping others
- Correct label: D | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Charity begins at home, so prioritize your family's needs above all else.
  - B. It is important to be generous and help those in need whenever possible.
  - C. One should always strive to be self-sufficient and avoid relying on others for support.
  - D. Giving to the community is a noble act, even if it means personal sacrifice.
- Correct label: A | Consensus: B (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Money that does not exist, no king can take from you.
  - B. One must adapt their methods when faced with an unusual problem.
  - C. A challenging situation will reveal the true skill of an individual.
  - D. Even a flawed vessel can serve a useful purpose if handled with care.
- Correct label: C | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A flawed vessel will always betray its handler's incompetence.
  - B. One's true character is revealed when faced with an impossible task.
  - C. The most difficult problems often have the simplest solutions.
  - D. A challenging situation will reveal the best approach to overcome it.
- Correct label: D | Consensus: B (frac=0.75)

## Distractor metrics

n_mcqs                            36.0000
avg_distractor_key_similarity      0.2982
std_distractor_key_similarity      0.1795
avg_pairwise_option_similarity     0.3125
std_pairwise_option_similarity     0.1611
option_length_mean                69.4000
option_length_cv                   0.2711
nli_replaced_total                16.0000
duplicate_options_count            0.0000

## Yoruba curation samples

Curated Yoruba items: 12
- **Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.**
  - Original: The neckless gourd will itself indicate to the farmer how to tie it up.
  - Curated:  The neckless gourd will itself indicate to the farmer how to tie it up.

## Root-cause synthesis

The v66 quick bundle moved the gates in the wrong direction. The headline metrics are worse than v65 on every gate except Yoruba correctness (now exactly 50%).

1. **Prompt hardening backfired.** Telling models to avoid generic reversals did not make them produce subtle, proverb-specific distractors. Instead, models still produced generic reversals and unrelated idioms ("Don't sell the skin before you've caught the bear", "The apple doesn't fall far from the tree", "Put your money where your mouth is"), and the few closer-to-correct attempts were caught by the NLI filter and replaced by low-quality corpus fallbacks.

2. **NLI replacements doubled (16 vs 8 in v65).** The mean `nli_replaced` went from 0.22 to 0.44. More paraphrase-like distractors were generated, sanitized away, and replaced by generic corpus fallbacks. Those replacements explain the jump in `partial` items (16 vs 9) and the rise in HCW (22.2% vs 11.1%).

3. **Length relaxation did not help overall.** `length_fallback` dropped from 4 to 2, but the freed items became `partial` because of NLI/corpus replacements. Net partial+fallback rose from 36.1% to 50.0%.

4. **Generator roster stabilised.** No mid-run substitutions; qwen, gemma-4, and gemini-2.5-flash stayed active for all 36 items. This removes one source of noise but does not fix distractor quality.

5. **English remains trivially easy.** 100% consensus correct, 96% mean consensus frac. The new prompt constraints are not sufficient to make English distractors hard.

The core problem is now unambiguous: **the corpus-based fallback sampler is the bottleneck.** Whenever a model produces a paraphrase, a length outlier, or a duplicate, the replacement is sampled from other proverb meanings. Those replacements are often generic, culturally mismatched, or obviously wrong, which either (a) makes the item too easy if the key survives or (b) creates confident-wrong consensus if the fallback distractor is plausible.

## Options for v67

| Option | Change | Expected effect | Risk |
|---|---|---|---|
| **A. LLM-based fallback distractor generator (recommended)** | Replace `semantically_distinct_negative_sample()` with a small-model call (`gpt-4.1-nano` or `gemini-2.5-flash`) that generates a single distractor given the correct meaning, target length, and a forbidden-paraphrase constraint. | Biggest impact on partial+fallback and HCW; replacements become proverb-specific hard negatives instead of random corpus meanings. | Adds cost per replacement (~$0.005 each); requires careful prompt to avoid paraphrases. |
| **B. Template-based distractor perturbation** | Generate fallback distractors by synthetically perturbing the correct meaning: change scope, agent, causal direction, or modality. Cheap and deterministic. | Low cost; may produce more consistent distractors. | Templates can be repetitive and may still leak meaning if not varied. |
| **C. Revert v66 prompt/length changes, keep dup fix** | Go back to v65 prompts and length thresholds; only keep the `dup_replaced` bookkeeping and the reordered generator pool. | Restores the better v65 baseline while keeping the low-noise roster. | Does not solve the fallback-sampler problem; gates still fail. |
| **D. Skip N=1 gates and scale to N=2/N=5** | Accept that N=1 is too noisy with only 3 proverbs and run a larger sample for interpretable metrics. | Gets real signal faster. | Violates the stated scaling rule and may burn budget on a still-broken pipeline. |

**Recommended v67 plan:** C first (revert prompt/length to v65 to restore the better baseline), then A (LLM-based fallback generator) on top. If cost allows, A alone can be tested directly.
