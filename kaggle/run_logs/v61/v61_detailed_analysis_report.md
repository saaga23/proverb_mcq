# v61 Kaggle Run — Detailed Analysis

- Run timestamp: 2026-06-20T19:27:22.225024+00:00
- Notebook version: 61
- N_PER_LANG: 1
- Cost: $0.1864 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash']
- Benched generators: []
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']
- Total MCQs: 36 (3 langs x 3 gens x 4 variants)

## Quality-gate evolution

| Gate | v58 | v59 | v60 | v61 | Target |
|---|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.23 | $0.1864 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | 47.2% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | 25.0% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | 47.2% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | 61.1% | — |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | 33.3% | ≥50% |

## Per-language consensus correctness

- Arabic: 58.3% (n=12)  — mean consensus frac 0.81
- English: 91.7% (n=12)  — mean consensus frac 0.90
- Yoruba: 33.3% (n=12)  — mean consensus frac 0.67

## Generation status breakdown

generation_status
generated          19
partial            10
length_fallback     6
parse_fallback      1
Name: count, dtype: int64

### By generator

generation_status        generated  length_fallback  parse_fallback  partial
generator_model                                                             
google/gemini-2.5-flash          7                2               0        3
google/gemma-4-31b-it            5                1               1        5
qwen/qwen3.7-max                 7                3               0        2

### By variant

generation_status          generated  length_fallback  parse_fallback  partial
variant                                                                       
adversarial-hard-negative          3                2               0        4
adversarial-length-locked          4                3               0        2
overgenerate-select                5                1               1        2
taxonomy-guided                    7                0               0        2

### By language

generation_status  generated  length_fallback  parse_fallback  partial
language                                                              
Arabic                     8                3               1        0
English                    6                1               0        5
Yoruba                     5                2               0        5

## Per-variant consensus accuracy (language=ALL)

        generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
       qwen/qwen3.7-max adversarial-length-locked  3            0.333333             0.416667 REVIEW
       qwen/qwen3.7-max adversarial-hard-negative  3            0.666667             0.916667   FAIL
       qwen/qwen3.7-max           taxonomy-guided  3            0.666667             0.583333   FAIL
       qwen/qwen3.7-max       overgenerate-select  3            0.666667             0.916667   FAIL
  google/gemma-4-31b-it adversarial-length-locked  3            0.333333             0.833333 REVIEW
  google/gemma-4-31b-it adversarial-hard-negative  3            0.666667             1.000000   FAIL
  google/gemma-4-31b-it           taxonomy-guided  3            0.666667             0.666667   FAIL
  google/gemma-4-31b-it       overgenerate-select  3            1.000000             0.916667   FAIL
google/gemini-2.5-flash adversarial-length-locked  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash adversarial-hard-negative  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash           taxonomy-guided  3            0.333333             0.916667 REVIEW
google/gemini-2.5-flash       overgenerate-select  3            0.666667             0.666667   FAIL

## Length-fallback deep dive

Total length_fallback items: 6 / 36 (16.7%)

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=84, B=53, C=68, D=52 (median=60)
  - A. (84 chars, 1.39x median) Individuals must support their own relatives before donating to public institutions.  **OUT OF ±30%**
  - B. (53 chars, 0.88x median) Little enemies and little wounds must not be despised
  - C. (68 chars, 1.12x median) Everyone is critical of the flaws of others, but blind to their own.
  - D. (52 chars, 0.86x median) If you’re unable to reward, then make sure to thank.

### qwen_qwen3.7-max_adversarial-length-locked_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
- Option lengths: A=53, B=47, C=51, D=50 (median=50)
  - A. (53 chars, 1.05x median) We must constantly struggle to get through our lives.
  - B. (47 chars, 0.93x median) There are limits to what wealth can do for you.
  - C. (51 chars, 1.01x median) True friends are those who help in difficult times.
  - D. (50 chars, 0.99x median) Painful struggles forge enduring mental fortitude.

### google_gemma-4-31b-it_adversarial-length-locked_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=65, B=71, C=43, D=54 (median=60)
  - A. (65 chars, 1.09x median) One should not attempt to scare an old [woman] with a huge penis.
  - B. (71 chars, 1.19x median) One is never so poor that one does not own one single item of clothing.
  - C. (43 chars, 0.72x median) Only coolness come out of the fish’s mouth.
  - D. (54 chars, 0.91x median) The neckless gourd will show the farmer how to tie it.

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=52, B=73, C=66, D=48 (median=59)
  - A. (52 chars, 0.88x median) I curse my own child but I hate whoever says “amen.”
  - B. (73 chars, 1.24x median) One must provide for their own family before giving to outside charities.
  - C. (66 chars, 1.12x median) People who don’t walk in your shoes can’t understand your journey.
  - D. (48 chars, 0.81x median) Choose a partner/ friend before choosing a path.

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=35, B=50, C=33, D=59 (median=42)
  - A. (35 chars, 0.82x median) It's no use crying over spilt milk.
  - B. (50 chars, 1.18x median) Glad it is over! I shall send you a sympathy card.
  - C. (33 chars, 0.78x median) Do good and cast it into the sea.
  - D. (59 chars, 1.39x median) Family needs should be prioritized over external donations.  **OUT OF ±30%**

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Option lengths: A=74, B=71, C=58, D=68 (median=70)
  - A. (74 chars, 1.06x median) Nursing mother, make the herbal decoction in good time; the day is waning.
  - B. (71 chars, 1.02x median) This world [is] something to be handled momentarily and then let go of.
  - C. (58 chars, 0.83x median) One does not dive under water without knowing how to swim.
  - D. (68 chars, 0.98x median) The gourd without a neck will show the farmer how it should be tied.

## Partial items deep dive

Total partial items: 10 / 36

### google_gemini-2.5-flash_adversarial-length-locked_English_1
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Difficult experiences inevitably lead to greater physical strength.
  - B. Challenges contribute to personal growth and fortitude.
  - C. A person of experience is difficult to fool or manipulate.
  - D. Suffering is a necessary component of all human achievement.

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The destiny of the innocent, the destiny of the person who thought no ill, will be the death of the person who spreads evil reports about another person.
  - B. A child who carries a very difficult destiny will inevitably lead the diviner to see the specific ritual required to bless them.
  - C. A person who lacks conventional qualities will inevitably show others the exact method required to handle them.
  - D. A leader who hoards the wealth of the town will inevitably teach the people the exact strategy required to depose them.

### google_gemma-4-31b-it_adversarial-hard-negative_English_1
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Conciseness enhances intelligence.
  - B. Adversity builds resilience.
  - C. Pain eliminates all weakness.
  - D. Survival guarantees improvement.

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Destitution does not afflict the husband and spare his children; the poverty-ridden person does not have relatives.
  - B. A person losing family ties must rely on the village elders to secure their place in society.
  - C. An individual with obvious flaws must be left entirely alone to figure out their own survival.
  - D. A person lacking standard advantages must show others the unique way they need to be handled.

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The neckless gourd will show the farmer how to tie it.
  - B. Is it just morning now? The old man is striv ing to make two hundred heaps a day.
  - C. The gourd's shape dictates how the farmer must tie it.
  - D. It is the leavings from the farmer’s farm table that the king eats on his throne.

### google_gemini-2.5-flash_adversarial-hard-negative_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A difficult task will eventually show the laborer the best way to approach it.
  - B. A problem will reveal its own solution to the one who seeks to resolve it.
  - C. Ever in a muddy state is how one finds the bath place.
  - D. An obstacle, through its very form, will instruct the person on how to manage it.

### google_gemma-4-31b-it_taxonomy-guided_English_1
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Love will overcome hardships or interference from others.
  - B. Consistent effort leads to eventual success
  - C. Overcoming hardships increases one's inner strength
  - D. Every challenging experience guarantees growth

### google_gemma-4-31b-it_taxonomy-guided_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Be his or her head oversized or deformed, one’s own thing is one’s own.
  - B. The flaw in a thing reveals the method needed to fix it.
  - C. The elder's wisdom shows the youth how to plant crops.
  - D. No carver of mortars can do a thing to the banana stem. I

### google_gemma-4-31b-it_overgenerate-select_English_1
- Generator: google/gemma-4-31b-it | Variant: overgenerate-select | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Survival ensures immortality.
  - B. Pain eliminates future weakness.
  - C. Don't criticize gifts.
  - D. Adversity builds resilience.

### google_gemini-2.5-flash_overgenerate-select_English_1
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Difficult experiences can lead to personal growth.
  - B. Survival is the ultimate measure of strength.
  - C. A person can’t change their fundamental nature.
  - D. Suffering is an unavoidable part of life.

## Parse-fallback reasons

- **google/gemma-4-31b-it / adversarial-length-locked / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=['Charity begins at home.', 'Faith requires action.', 'Family values endure.', 'Giving brings rewards.']
- **google/gemma-4-31b-it / overgenerate-select / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=['Charity begins at home', 'Family needs outweigh public duty', 'Religious devotion requires sacrifice', 'Home and temple are equal in value']

## High-consensus-wrong items

Count: 9 / 36 (25.0%)

### google_gemma-4-31b-it_adversarial-length-locked_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Offer your help to the needy.
  - B. Prioritize your own family first.
  - C. Keep your secrets within walls.
  - D. Build a home before a temple.
- Correct label: B | Consensus: A (frac=0.75)

### google_gemma-4-31b-it_adversarial-length-locked_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. One should not attempt to scare an old [woman] with a huge penis.
  - B. One is never so poor that one does not own one single item of clothing.
  - C. Only coolness come out of the fish’s mouth.
  - D. The neckless gourd will show the farmer how to tie it.
- Correct label: D | Consensus: B (frac=0.75)

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. It's no use crying over spilt milk.
  - B. Glad it is over! I shall send you a sympathy card.
  - C. Do good and cast it into the sea.
  - D. Family needs should be prioritized over external donations.
- Correct label: D | Consensus: A (frac=1.00)

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Destitution does not afflict the husband and spare his children; the poverty-ridden person does not have relatives.
  - B. A person losing family ties must rely on the village elders to secure their place in society.
  - C. An individual with obvious flaws must be left entirely alone to figure out their own survival.
  - D. A person lacking standard advantages must show others the unique way they need to be handled.
- Correct label: D | Consensus: A (frac=1.00)

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The neckless gourd will show the farmer how to tie it.
  - B. Is it just morning now? The old man is striv ing to make two hundred heaps a day.
  - C. The gourd's shape dictates how the farmer must tie it.
  - D. It is the leavings from the farmer’s farm table that the king eats on his throne.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. One should prioritize their family's needs before assisting others.
  - B. Donations to religious institutions are less important than family expenses.
  - C. It is important to manage household finances responsibly to avoid debt.
  - D. Giving to the community is a noble act, regardless of personal circumstances.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemma-4-31b-it_taxonomy-guided_English_1
- Generator: google/gemma-4-31b-it | Variant: taxonomy-guided | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Love will overcome hardships or interference from others.
  - B. Consistent effort leads to eventual success
  - C. Overcoming hardships increases one's inner strength
  - D. Every challenging experience guarantees growth
- Correct label: C | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. One's unique characteristics will eventually become apparent to others.
  - B. Even the most challenging situations can be overcome with persistent effort.
  - C. A person's inherent limitations will reveal the appropriate way to assist them.
  - D. A person without proper guidance will struggle to find their place in the community.
- Correct label: C | Consensus: A (frac=0.75)

### qwen_qwen3.7-max_overgenerate-select_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: overgenerate-select | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Taking from the public treasury for private use is a grave sin.
  - B. Sacred places of worship must not be burdened with worldly needs.
  - C. Hosting guests in your home is as virtuous as praying in public.
  - D. One should provide for their own family before giving to others.
- Correct label: D | Consensus: A (frac=1.00)

## Distractor metrics

n_mcqs                            36.0000
avg_distractor_key_similarity      0.2839
std_distractor_key_similarity      0.1674
avg_pairwise_option_similarity     0.3109
std_pairwise_option_similarity     0.1512
option_length_mean                61.8000
option_length_cv                   0.4185
nli_replaced_total                10.0000
duplicate_options_count            0.0000

## Root-cause synthesis

1. **Starters remain active and produce higher-quality output.** Consensus accuracy recovered to 61.1% (v58=60.0%, v60=48.9%) and HCW fell to 25.0% (from 28.9%).
2. **Partial+fallback is still 47.2%**, far above the 15% target. The length relaxation and semantic widening helped slightly, but the sanitizers (semantic/NLI/leak/length) still rewrite nearly half the generated distractors.
3. **Length_fallback is now 17%** (6/36), down from 31% in v60, but it clusters in adversarial-length-locked and qwen/qwen3.7-max. Some generated option sets have one very long option that pulls the median up and pushes the others out of ±30%.
4. **adversarial-hard-negative is the hardest variant to sanitize** — 3 generated, 2 length_fallback, 4 partial. Its semantically close distractors frequently violate length/semantic/leak constraints.
5. **English is now 91.7% correct**, which is excellent but drives perfect consensus up to 47.2%. The English options are too easy for the auditors; the distractors are not tempting enough.
6. **Yoruba is still the weakest language at 33.3%**, driven by literal/awkward gold meanings and a small sample (n=12).

## Options for v62

A. **Make length check even more lenient or smarter.** Instead of ±30% against the median of all four options, allow each distractor to be within ±30% of the closest other option, or skip length check entirely for items where all four options are within ±40%.
B. **Disable or drastically weaken the leak sanitizer for English.** The 80% token-overlap rule catches many legitimate hard negatives (e.g., changing one word in the correct meaning). Lower threshold to 0.90 for English, keep 0.80 for Arabic/Yoruba.
C. **Tune semantic band per language.** English distractors are being over-replaced; try default 0.88 and Yoruba 0.90.
D. **Replace adversarial-hard-negative or adversarial-length-locked with a variant that generates less brittle options.** Both have high partial+fallback rates.
E. **Yoruba rescue:** pre-process Yoruba gold meanings with a cheap LLM call to rewrite literal glosses into natural English before generating options.

**Recommended v62 combination:** A + B + E. A should immediately cut length_fallback; B should reduce English over-sanitization and partials; E is the only likely fix for the Yoruba floor.
