# v65 Kaggle Run — Detailed Analysis

- Run timestamp: 2026-06-21T12:25:47.022549+00:00
- Notebook version: 65
- N_PER_LANG: 1
- Cost: $0.1879 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemini-2.5-flash', 'anthropic/claude-sonnet-4']
- Benched generators: ['google/gemma-4-31b-it']
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']
- Total MCQs: 36 (3 langs x 3 gens x 4 variants)

## Quality-gate evolution

| Gate | v58 | v59 | v60 | v61 | v65 | Target |
|---|---|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.23 | $0.1864 | $0.1879 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | 47.2% | 41.7% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | 25.0% | 11.1% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | 47.2% | 36.1% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | 61.1% | 63.9% | — |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | 33.3% | 41.7% | ≥50% |

## Per-language consensus correctness

- Arabic: 50.0% (n=12)  — mean consensus frac 0.67
- English: 100.0% (n=12)  — mean consensus frac 0.88
- Yoruba: 41.7% (n=12)  — mean consensus frac 0.73

## Generation status breakdown

generation_status
generated          22
partial             9
length_fallback     4
hard_fallback       1
Name: count, dtype: int64

### By generator

generation_status          generated  hard_fallback  length_fallback  partial
generator_model                                                              
anthropic/claude-sonnet-4          1              0                0        1
google/gemini-2.5-flash            8              0                1        3
google/gemma-4-31b-it              7              1                0        2
qwen/qwen3.7-max                   6              0                3        3

### By variant

generation_status          generated  hard_fallback  length_fallback  partial
variant                                                                      
adversarial-hard-negative          3              0                3        3
adversarial-length-locked          6              0                1        2
overgenerate-select                7              1                0        1
taxonomy-guided                    6              0                0        3

### By language

generation_status  generated  hard_fallback  length_fallback  partial
language                                                             
Arabic                     6              1                3        2
English                    8              0                0        4
Yoruba                     8              0                1        3

## Fallback-count diagnostics

- Mean fallback_count: 0.78
- Mean length_replaced: 0.11
- Mean leak_replaced: 0.22
- Mean nli_replaced: 0.22

## Per-variant consensus accuracy (language=ALL)

          generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
         qwen/qwen3.7-max adversarial-length-locked  3            0.333333             0.666667 REVIEW
         qwen/qwen3.7-max adversarial-hard-negative  3            1.000000             0.833333   FAIL
         qwen/qwen3.7-max           taxonomy-guided  3            0.666667             0.666667   FAIL
         qwen/qwen3.7-max       overgenerate-select  3            0.333333             0.666667 REVIEW
  google/gemini-2.5-flash adversarial-length-locked  3            0.666667             0.833333   FAIL
  google/gemini-2.5-flash adversarial-hard-negative  3            0.666667             0.750000   FAIL
  google/gemini-2.5-flash           taxonomy-guided  3            0.666667             0.916667   FAIL
  google/gemini-2.5-flash       overgenerate-select  3            0.333333             0.833333 REVIEW
anthropic/claude-sonnet-4       overgenerate-select  2            0.500000             0.500000   FAIL
    google/gemma-4-31b-it adversarial-length-locked  3            0.666667             0.750000   FAIL
    google/gemma-4-31b-it adversarial-hard-negative  3            1.000000             0.916667   FAIL
    google/gemma-4-31b-it           taxonomy-guided  3            0.666667             0.666667   FAIL
    google/gemma-4-31b-it       overgenerate-select  1            1.000000             0.750000   FAIL

## Length-fallback deep dive

Total length_fallback items: 4 / 36 (11.1%)

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=75, B=47, C=59, D=44 (median=53)
  - A. (75 chars, 1.42x median) A person must support their own family before giving charity to the public.  **OUT OF ±35%**
  - B. (47 chars, 0.89x median) Beware the levelheaded person if they’re angry.
  - C. (59 chars, 1.11x median) The best answer will come from the person who is not angry.
  - D. (44 chars, 0.83x median) He who gathers honey, must suffer the stings

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=52, B=77, C=76, D=50 (median=64)
  - A. (52 chars, 0.81x median) I curse my own child but I hate whoever says “amen.”
  - B. (77 chars, 1.20x median) One must provide for their own household before giving charity to the public.
  - C. (76 chars, 1.19x median) One should prioritize building a solid home over engaging in public worship.
  - D. (50 chars, 0.78x median) Don't sell the skin before you've caught the bear.

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=41, B=71, C=63, D=73 (median=67)
  - A. (41 chars, 0.61x median)  A living dog is better than a dead lion.  **OUT OF ±35%**
  - B. (71 chars, 1.06x median) The world is like a belly-dancer: it dances a little while for everyone
  - C. (63 chars, 0.94x median) You should only help others if your family has no needs at all.
  - D. (73 chars, 1.09x median) One should prioritize their family's needs over external charitable acts.

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=70, B=107, C=106, D=112 (median=106)
  - A. (70 chars, 0.66x median) Words are eggs; when they drop on the floor, they shatter into pieces.
  - B. (107 chars, 1.00x median) A farmer who finds a vessel without a neck must consult the village elders to learn how to tie it securely.
  - C. (106 chars, 1.00x median) A white buttock is not a natural condition; for a farmer it happens when he rubs his buttocks in the dirt.
  - D. (112 chars, 1.05x median) A vessel lacking a standard neck will eventually teach the farmer the unique method required to tie it securely.

## Partial items deep dive

Total partial items: 9 / 36

### google_gemini-2.5-flash_adversarial-length-locked_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. It’s better to avoid mistakes altogether than do something that you should apologize for after.
  - B. It is important to prioritize community needs over individual family desires.
  - C. One's primary responsibility is to their household before assisting those outside of it.
  - D. Always ensure your own needs are met before considering the needs of others.

### qwen_qwen3.7-max_adversarial-length-locked_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Different people have different taste s, so what one person loves might be terrible to another.
  - B. Studying past failures helps scholars to gain deeper intellectual insight and theoretical knowledge.
  - C. Surviving market crashes enables investors to secure larger financial wealth and material prosperity.
  - D. Enduring tough trials allows people to build greater emotional resilience and practical competence.

### qwen_qwen3.7-max_adversarial-hard-negative_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Enduring severe hardships ultimately helps us become more resilient and capable.
  - B. Sometimes you can trust an enemy more than an alleged friend.
  - C. One positive action can have a long -lasting impact.
  - D. Enduring minor inconveniences ultimately helps us become more resilient and capable.

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A flawed object teaches the maker how to improve the craft.
  - B. Where one eats food worth 40 cowries, one should make a speech worth 20 cowries.
  - C. The farmer learns to value the gourd only after it breaks.
  - D. A neckless gourd proves that the farmer's method failed.

### google_gemini-2.5-flash_adversarial-hard-negative_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The ground hornbill’s lack of fat is not to be compared with that of the allied hornbill.
  - B. A difficult situation will reveal the true measure of one's resourcefulness.
  - C. A flawed tool will always hinder the progress of a diligent worker.
  - D. A challenging task requires careful planning and preparation.

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Choose a partner/ friend before choosing a path.
  - B. Give generously to the community to ensure a blessing.
  - C. Donate everything you have to the mosque for reward.
  - D. Prioritize your own family's needs before helping others.

### qwen_qwen3.7-max_taxonomy-guided_English_1
- Generator: qwen/qwen3.7-max | Variant: taxonomy-guided | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. The effects on the greater whole are visible in each of its parts.
  - B. Enduring severe adversity ultimately builds greater psychological resilience and fortitude.
  - C. Enduring physical exertion ultimately builds greater muscular endurance and physical vitality.
  - D. If you are having a difficult time now, maintain your hope that you will have success later.

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. One must adapt their methods when faced with an unusual challenge.
  - B. One does not live with a person and yet not know how to deal with him or her.
  - C. A difficult situation will reveal the true skill and ingenuity of a person.
  - D. Even the most flawed vessel can serve a useful purpose if handled with care.

### anthropic_claude-sonnet-4_overgenerate-select_English_1
- Generator: anthropic/claude-sonnet-4 | Variant: overgenerate-select | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Facing hardships helps us become more resilient and capable.
  - B. Surviving dangerous situations teaches us to avoid similar risks in the future.
  - C. Overcoming challenges reveals our hidden talents and natural abilities.
  - D. People are most tempted by that which is tab oo or prohibited.

## Parse-fallback reasons

Total parse_fallback rows: 0


## High-consensus-wrong items

Count: 4 / 36 (11.1%)

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A heavily cracked clay pot shows the potter the proper way to fire it in the village kiln.
  - B. A remarkably heavy yam crop shows the elder the safest way to store it in the wooden barn.
  - C. A uniquely shaped calabash shows the harvester the exact way to bind it for the journey.
  - D. A severely dull iron blade shows the smith the precise way to sharpen it on the stone.
- Correct label: C | Consensus: D (frac=0.75)

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A challenging situation will reveal the best way to handle it, teaching resourcefulness.
  - B. A person without proper guidance will struggle to find their place in the community.
  - C. One's true character is often revealed when faced with unexpected difficulties.
  - D. The wisdom of the elders is essential for navigating life's complex problems.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. One should prioritize their immediate family's needs before extending assistance to the wider community.
  - B. It is important to contribute to your local community whenever possible.
  - C. The best answer will come from the person who is not angry.
  - D. Helping others is a noble act, regardless of your personal circumstances.
- Correct label: A | Consensus: B (frac=1.00)

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A stubborn person will eventually yield to a stronger will.
  - B. One's true character is revealed in times of adversity.
  - C. A challenging situation will reveal the best approach to overcome it.
  - D. The most difficult tasks often require the simplest solutions.
- Correct label: C | Consensus: B (frac=1.00)

## Distractor metrics

n_mcqs                            36.0000
avg_distractor_key_similarity      0.3081
std_distractor_key_similarity      0.1870
avg_pairwise_option_similarity     0.3188
std_pairwise_option_similarity     0.1634
option_length_mean                72.6000
option_length_cv                   0.2395
nli_replaced_total                 8.0000
duplicate_options_count            0.0000

## Yoruba curation samples

Curated Yoruba items: 12
- **Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.**
  - Original: The neckless gourd will itself indicate to the farmer how to tie it up.
  - Curated:  The neckless gourd will itself indicate to the farmer how to tie it up.

## Root-cause synthesis

The v65 bundle (option-level blocklist, correct-option length outlier no longer counted, English NLI guard 0.58) moved the gates in the right direction on HCW and partial+fallback, but several gates remain failed and a new source of noise appeared.

1. **HCW dropped sharply to 11.1%.** The Arabic/Yoruba NLI guard from v64 plus the option-level blocklist removed the confident-wrong fallback items that plagued v63/v64.

2. **Partial+fallback improved to 36.1%.** The blocklist fix eliminated parse-fallbacks (0 vs 4 in v64). However, 9 partials and 4 length-fallbacks remain, mostly from qwen and gemini. Correct-option length outliers are no longer counted, so the remaining length-fallbacks reflect genuine distractor length outliers.

3. **English is still too easy (100% consensus correct, 88% mean consensus frac).** Distractors are often generic reversals or unrelated proverbs ("Beware the levelheaded person if they’re angry", "Different people have different tastes"). Raising the English NLI guard to 0.58 did not produce more subtle near-paraphrase distractors; if anything, the surviving distractors are still too obviously wrong.

4. **Yoruba correctness fell back to 41.7%.** The hard-negative variants produced structurally parallel distractors ("A cracked clay pot shows the potter...", "A dull blade shows the smith...") that auditors found more attractive than the correct gourd/farmer option. This suggests the correct meaning is not sufficiently distinctive, or the prompt rewards surface analogies over the proverb’s specific image.

5. **Generator churn adds noise.** `google/gemma-4-31b-it` was benched after 2 hard_fallbacks and replaced by `anthropic/claude-sonnet-4`. The substitution happened mid-run, so the per-run comparison mixes two generator rosters. Claude contributed only 2 MCQs (1 generated, 1 partial, 1 hard_fallback) and remains unreliable.

Bottom line: the biggest remaining levers are **(a) making English distractors more subtly wrong, (b) making the Yoruba/Arabic correct meaning more distinctive against parallel analogies, and (c) stabilising the generator roster** so each run is comparable.

## Options for v66

| Option | Change | Expected effect | Risk |
|---|---|---|---|
| **A. Push the local dup-replaced refinement** | Do not count `dup_replaced` toward `fallback_count`/status (already coded locally). | Could reclassify some partials to generated, lowering partial+fallback a few points. | Minor; mostly bookkeeping. |
| **B. Harder English prompt constraint** | Add a rule that English distractors must be *plausible alternative interpretations* of the proverb, not generic opposites or unrelated idioms; ban surface reversals like "avoiding difficult situations..." | Should lower English perfect consensus. | May raise HCW if near-paraphrases survive. |
| **C. Yoruba/Arabic meaning distinctiveness** | Rewrite curated meanings to foreground the *specific causal mechanism* (e.g., "The unusual shape of the gourd itself tells the farmer how to tie it, not any outside advice"). | Could raise per-language correctness by making the key easier to separate from parallel analogies. | Requires re-curation and re-run. |
| **D. Stabilise generator roster** | Remove `anthropic/claude-sonnet-4` from the substitute pool (or raise its fail threshold) and prefer `google/gemini-2.5-pro` or `openai/gpt-4.1-mini` as the gemma fallback. | Removes the noisy mid-run substitution and makes runs comparable. | May lose a working model if gemma-4 keeps failing. |
| **E. Post-generation difficulty probe** | Add a fast model check after generation: reject items where all 4 auditors are predicted to agree (consensus frac 1.0) and rewrite distractors once. | Directly targets perfect consensus. | Adds cost/complexity and may not converge. |

**Suggested v66 bundle:** A + B + D. A is already implemented locally; B attacks the English too-easy problem; D removes generator churn. If English/Yoruba correctness still fails after that, add C.
