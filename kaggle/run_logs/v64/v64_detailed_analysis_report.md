# v64 Kaggle Run — Detailed Analysis

- Run timestamp: 2026-06-21T11:02:18.472325+00:00
- Notebook version: 64
- N_PER_LANG: 1
- Cost: $0.1703 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash']
- Benched generators: []
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']
- Total MCQs: 36 (3 langs x 3 gens x 4 variants)

## Quality-gate evolution

| Gate | v58 | v59 | v60 | v61 | v64 | Target |
|---|---|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.23 | $0.1864 | $0.1703 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | 47.2% | 47.2% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | 25.0% | 19.4% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | 47.2% | 41.7% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | 61.1% | 66.7% | — |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | 33.3% | 50.0% | ≥50% |

## Per-language consensus correctness

- Arabic: 58.3% (n=12)  — mean consensus frac 0.67
- English: 91.7% (n=12)  — mean consensus frac 0.94
- Yoruba: 50.0% (n=12)  — mean consensus frac 0.81

## Generation status breakdown

generation_status
generated          21
partial             7
length_fallback     4
parse_fallback      4
Name: count, dtype: int64

### By generator

generation_status        generated  length_fallback  parse_fallback  partial
generator_model                                                             
google/gemini-2.5-flash          6                0               4        2
google/gemma-4-31b-it            8                1               0        3
qwen/qwen3.7-max                 7                3               0        2

### By variant

generation_status          generated  length_fallback  parse_fallback  partial
variant                                                                       
adversarial-hard-negative          2                2               1        4
adversarial-length-locked          4                2               1        2
overgenerate-select                8                0               1        0
taxonomy-guided                    7                0               1        1

### By language

generation_status  generated  length_fallback  parse_fallback  partial
language                                                              
Arabic                     6                1               4        1
English                    8                2               0        2
Yoruba                     7                1               0        4

## Fallback-count diagnostics

- Mean fallback_count: 0.78
- Mean length_replaced: 0.14
- Mean leak_replaced: 0.28
- Mean nli_replaced: 0.28

## Per-variant consensus accuracy (language=ALL)

        generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
       qwen/qwen3.7-max adversarial-length-locked  3            0.666667             0.833333   FAIL
       qwen/qwen3.7-max adversarial-hard-negative  3            1.000000             0.583333   FAIL
       qwen/qwen3.7-max           taxonomy-guided  3            1.000000             0.916667   FAIL
       qwen/qwen3.7-max       overgenerate-select  3            0.333333             0.750000 REVIEW
  google/gemma-4-31b-it adversarial-length-locked  3            0.666667             0.750000   FAIL
  google/gemma-4-31b-it adversarial-hard-negative  3            0.666667             0.916667   FAIL
  google/gemma-4-31b-it           taxonomy-guided  3            1.000000             0.833333   FAIL
  google/gemma-4-31b-it       overgenerate-select  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash adversarial-length-locked  3            0.333333             0.916667 REVIEW
google/gemini-2.5-flash adversarial-hard-negative  3            0.333333             0.750000 REVIEW
google/gemini-2.5-flash           taxonomy-guided  3            1.000000             0.750000   FAIL
google/gemini-2.5-flash       overgenerate-select  3            0.333333             0.833333 REVIEW

## Length-fallback deep dive

Total length_fallback items: 4 / 36 (11.1%)

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=92, B=49, C=75, D=59 (median=67)
  - A. (92 chars, 1.37x median) A person must prioritize providing for their own household before donating to the community.  **OUT OF ±35%**
  - B. (49 chars, 0.73x median) Let's wait and hold to see what the future holds.
  - C. (75 chars, 1.12x median) A person of two minds is a liar, and a person of three minds is a hypocrite
  - D. (59 chars, 0.88x median) The best answer will come from the person who is not angry.

### qwen_qwen3.7-max_adversarial-length-locked_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
- Option lengths: A=101, B=97, C=58, D=101 (median=99)
  - A. (101 chars, 1.02x median) As art is the outcome of creative imagination, people who lack this vision may fail to appreciate it.
  - B. (97 chars, 0.98x median) People who do unscrupulous or wrongful actions may become themselves victims of a similar action.
  - C. (58 chars, 0.59x median) People abandon a failing enterprise when problems develop.  **OUT OF ±35%**
  - D. (101 chars, 1.02x median) Enduring severe hardships allows people to develop greater emotional resilience and practical skills.

### qwen_qwen3.7-max_adversarial-hard-negative_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
- Option lengths: A=83, B=99, C=88, D=74 (median=86)
  - A. (83 chars, 0.97x median) Surviving difficult challenges ultimately builds our resilience and inner strength.
  - B. (99 chars, 1.16x median) If you are determined enough, you can find a way to achieve what you want, even if it is difficult.
  - C. (88 chars, 1.03x median) Some inconvenien t situations are beyond our control and will only get better with time.
  - D. (74 chars, 0.87x median) Sometimes, escaping a difficult situation only leads to a worse situation.

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=61, B=57, C=81, D=62 (median=62)
  - A. (61 chars, 0.99x median) A flawed vessel teaches the farmer how to secure it properly.
  - B. (57 chars, 0.93x median) The shin forces the stream to speak out. 380 human nature
  - C. (81 chars, 1.32x median) It is the leavings from the farmer’s farm table that the king eats on his throne.
  - D. (62 chars, 1.01x median) Only people like monkeys have their cloth ing torn by monkeys.

## Partial items deep dive

Total partial items: 7 / 36

### google_gemma-4-31b-it_adversarial-length-locked_English_1
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Facing hardships helps us become more resilient and capable.
  - B. Enduring pain allows us to ignore future physical injuries.
  - C. Surviving danger ensures that we avoid similar accidents.
  - D. Intimacy can cause us to lose our regard.

### google_gemma-4-31b-it_adversarial-length-locked_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Whoever conceals a disease is beyond help from a doctor.
  - B. A leaking gourd shows the need for a better harvest.
  - C. A small vessel teaches the farmer how to plant seeds.
  - D. A flawed vessel reveals the skill of the one who mends it.

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Good health is a crown worn by the healthy that only the ill can see.
  - B. A person must provide for their own household before giving charity to the community.
  - C. Religious institutions are strictly forbidden from accepting donations a family needs.
  - D. The daily needs of a private home are far too sacred to be fulfilled by public funds.

### google_gemma-4-31b-it_adversarial-hard-negative_English_1
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Surviving a crisis ensures we avoid future difficulties.
  - B. Facing hardships helps us become more resilient and capable.
  - C. Life is full of surprises and the unexpected.
  - D. Overcoming a trauma removes our vulnerability to pain.

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. When it comes to frying, the palm weevil will contract.
  - B. A stubborn vessel will quickly shatter if the farmer tries to force a normal knot.
  - C. Whoever gives birth to a beautiful girl gives birth to trouble.
  - D. A flawed vessel forces the skilled farmer to invent a new method for securing it.

### google_gemini-2.5-flash_adversarial-hard-negative_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The person who makes off with one’s daugh ter will think nothing of making off with one’s wife.
  - B. A difficult situation will reveal the true measure of one's resourcefulness.
  - C. A flawed tool will always hinder the progress of a diligent worker.
  - D. A challenging task requires careful planning and preparation.

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. One must adapt their methods when faced with an unusual challenge.
  - B. We know not what God will do’’ keeps one from committing suicide.
  - C. A difficult situation will reveal the true skill and ingenuity of a person.
  - D. Even the most flawed vessel can serve a useful purpose if handled with care.

## Parse-fallback reasons

Total parse_fallback rows: 5

- **google/gemini-2.5-flash / adversarial-length-locked / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=["One should prioritize their immediate family's needs before assisting those outside their household.", 'It is important to contribute to community projects before focusing on personal matters.', 'Charity begins at home, but extends equally to all members of society.', 'Family obligations should always take precedence over religious duties.']
- **google/gemini-2.5-flash / adversarial-length-locked / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=["One should prioritize their immediate family's needs before assisting those outside their household.", 'It is important to contribute to community projects before focusing on personal matters.', 'Charity begins at home, but extends equally to all members of society.', 'Family obligations should always take precedence over religious duties.']
- **google/gemini-2.5-flash / adversarial-hard-negative / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=["One should prioritize their family's needs over external charitable acts.", 'Charity begins at home, but should not end there.', 'It is important to ensure your family is well-provided for before helping others.', 'You should only help others if your family has no needs at all.']
- **google/gemini-2.5-flash / taxonomy-guided / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=["One should prioritize their immediate family's needs before extending assistance to the wider community.", 'It is important to contribute to your local community whenever possible.', 'Charity begins at home, but it should not end there.', 'Helping others is a noble act, regardless of your personal circumstances.']
- **google/gemini-2.5-flash / overgenerate-select / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=["Charity begins at home, so prioritize your family's needs.", 'One should always give to the community before personal gain.', 'It is important to share your wealth with those less fortunate.', 'Focus on your spiritual duties before worldly responsibilities.']

## High-consensus-wrong items

Count: 7 / 36 (19.4%)

### google_gemini-2.5-flash_adversarial-length-locked_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. The best answer will come from the person who is not angry.
  - B. With care do you realize your opportunities.
  - C. A person should take care of their own family before offering help to others.
  - D. After black clouds, clear weather./ Slow and steady wins the race.

- Correct label: C | Consensus: A (frac=0.75)

### qwen_qwen3.7-max_adversarial-length-locked_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. As art is the outcome of creative imagination, people who lack this vision may fail to appreciate it.
  - B. People who do unscrupulous or wrongful actions may become themselves victims of a similar action.
  - C. People abandon a failing enterprise when problems develop.
  - D. Enduring severe hardships allows people to develop greater emotional resilience and practical skills.
- Correct label: D | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A challenging situation will reveal the best way to handle it, teaching resourcefulness.
  - B. A person without proper guidance will struggle to find their place in the community.
  - C. One's true character is often revealed when faced with unexpected difficulties.
  - D. The wisdom of the elders is essential for navigating life's complex problems.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. I curse my own child, but I hate whoever says “amen.”
  - B. In haste there is regret, but in patience and care there is peace and safety.
  - C. The stupid might want to help you, but they just ended up hurting you.
  - D. A person should take care of their own family before offering help to others.
- Correct label: D | Consensus: B (frac=0.75)

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A flawed vessel teaches the farmer how to secure it properly.
  - B. The shin forces the stream to speak out. 380 human nature
  - C. It is the leavings from the farmer’s farm table that the king eats on his throne.
  - D. Only people like monkeys have their cloth ing torn by monkeys.
- Correct label: A | Consensus: C (frac=0.75)

### qwen_qwen3.7-max_overgenerate-select_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Any barren yam mound shows the cultivator that the earth spirits withhold favor.
  - B. Every uniquely shaped calabash forces the harvester to invent a new binding method.
  - C. One cracked clay pot eventually reveals which village well is starting to run dry.
  - D. Only after the first blade shatters does the blacksmith learn to temper the hoe.
- Correct label: B | Consensus: D (frac=1.00)

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A stubborn person will eventually yield to a stronger will.
  - B. One's true character is revealed in times of adversity.
  - C. The most difficult tasks often require the simplest solutions.
  - D. A challenging situation will reveal the best approach to overcome it.
- Correct label: D | Consensus: B (frac=1.00)

## Distractor metrics

n_mcqs                            36.0000
avg_distractor_key_similarity      0.2814
std_distractor_key_similarity      0.1779
avg_pairwise_option_similarity     0.3254
std_pairwise_option_similarity     0.1539
option_length_mean                71.0000
option_length_cv                   0.2613
nli_replaced_total                10.0000
duplicate_options_count            0.0000

## Yoruba curation samples

Curated Yoruba items: 12
- **Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.**
  - Original: The neckless gourd will itself indicate to the farmer how to tie it up.
  - Curated:  The neckless gourd will itself indicate to the farmer how to tie it up.

## Root-cause synthesis

The A+B+C+D bundle moved the headline HCW and per-language correctness gates in the right direction, but the run is still failing on the structural gates (perfect consensus, partial+fallback). Root causes are now sharper:

1. **Blocklist is over-firing on the correct option.** Four of the five parse-fallback rows come from the Arabic proverb whose curated gold meaning is literally "Charity begins at home." `has_generic_english_idiom()` flags the *correct* option and rejects the whole MCQ, forcing a low-quality corpus fallback. The blocklist should only apply to distractors.

2. **Correct-option length is counted as a fallback.** The length check flags the correct meaning when it is a median outlier and adds it to `length_replaced`, bumping otherwise acceptable MCQs into `length_fallback` status. Distractor parity matters; penalising the correct option for being longer is a classification artefact, not a quality issue.

3. **English distractors are still too obviously wrong.** English consensus accuracy is 91.7% and almost every English item reaches perfect or near-perfect consensus. The distractors are generic reversals ("avoiding difficult situations...", "life's struggles are best ignored") rather than subtle near-paraphrases, so auditors unanimously identify the key.

4. **Yoruba correctness improved to 50% but remains fragile.** Several HCW items are either partial/fallback rows with incoherent corpus distractors or generated rows where abstract truisms ("a difficult situation will reveal...") attract consensus away from the concrete gourd/farmer meaning.

5. **NLI replacements increased (10 vs 5 in v63) and helped HCW.** Lowering the Arabic/Yoruba embedding guard to 0.45 did reduce confident-wrong consensus; it did not cause the rise in partial+fallback.

In short: the biggest drag on the gates is no longer generation quality but **over-aggressive whole-item rejection** (blocklist + length classification). Fixing those should drop partial+fallback materially and may also reduce HCW by removing low-quality fallback distractors.

## Recommended options for v65

| Option | Change | Expected effect | Risk |
|---|---|---|---|
| **A. Option-level blocklist (recommended)** | Skip `opts[0]` in `has_generic_english_idiom()`; if a *distractor* contains a blocked idiom, replace only that option via `semantically_distinct_negative_sample`, do not raise `parse_fallback`. | Eliminates the 4 Arabic parse-fallbacks; keeps blocklist protection for distractors. | Replacement distractor may still be generic if corpus is thin. |
| **B. Stop counting correct-option length outliers** | Exclude `opts[0]` from `length_replaced` and from the `fallback_count` status logic. Continue replacing outlier distractors. | Re-classifies several `length_fallback` rows to `generated`/`partial`, dropping partial+fallback. | A very long correct option can become a length giveaway; but length ratio to median is already bounded by generation. |
| **C. Raise English NLI guard** | Increase `NLI_EMBEDDING_GUARD_BY_LANGUAGE["english"]` from 0.55 to ~0.60 so more near-paraphrase distractors survive for English proverbs. | Should lower perfect consensus on English by making distractors more plausible. | May raise English HCW if near-paraphrases become too attractive. |
| **D. Harder English prompt constraint** | Add an explicit instruction that English distractors must be *plausible alternative interpretations* of the proverb, not generic opposites or life advice. | Could improve distractor specificity without touching filters. | Model compliance varies; may increase partial if models struggle. |

**Suggested v65 bundle:** A + B + a small C (raise English guard to 0.58). This directly attacks the 41.7% partial+fallback rate and the English too-easy problem while keeping the Arabic/Yoruba NLI gains that improved HCW.
