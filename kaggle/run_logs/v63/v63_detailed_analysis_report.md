# v63 Kaggle Run — Detailed Analysis

- Run timestamp: 2026-06-21T07:42:39.884273+00:00
- Notebook version: 63
- N_PER_LANG: 1
- Cost: $0.1909 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemini-2.5-flash', 'anthropic/claude-sonnet-4']
- Benched generators: ['google/gemma-4-31b-it']
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']
- Total MCQs: 36 (3 langs x 3 gens x 4 variants)

## Quality-gate evolution

| Gate | v58 | v59 | v60 | v61 | v63 | Target |
|---|---|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.23 | $0.1864 | $0.1909 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | 47.2% | 52.8% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | 25.0% | 33.3% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | 47.2% | 36.1% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | 61.1% | 55.6% | — |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | 33.3% | 25.0% | ≥50% |

## Per-language consensus correctness

- Arabic: 41.7% (n=12)  — mean consensus frac 0.81
- English: 100.0% (n=12)  — mean consensus frac 0.96
- Yoruba: 25.0% (n=12)  — mean consensus frac 0.73

## Generation status breakdown

generation_status
generated          22
partial             9
length_fallback     3
parse_fallback      1
hard_fallback       1
Name: count, dtype: int64

### By generator

generation_status          generated  hard_fallback  length_fallback  parse_fallback  partial
generator_model                                                                              
anthropic/claude-sonnet-4          2              0                0               0        4
google/gemini-2.5-flash            9              0                0               0        3
google/gemma-4-31b-it              3              1                0               1        1
qwen/qwen3.7-max                   8              0                3               0        1

### By variant

generation_status          generated  hard_fallback  length_fallback  parse_fallback  partial
variant                                                                                      
adversarial-hard-negative          3              1                2               0        3
adversarial-length-locked          7              0                1               1        0
overgenerate-select                7              0                0               0        2
taxonomy-guided                    5              0                0               0        4

### By language

generation_status  generated  hard_fallback  length_fallback  parse_fallback  partial
language                                                                             
Arabic                     7              0                2               1        2
English                    9              0                1               0        2
Yoruba                     6              1                0               0        5

## Fallback-count diagnostics

- Mean fallback_count: 0.75
- Mean length_replaced: 0.00
- Mean leak_replaced: 0.00
- Mean nli_replaced: 0.14

## Per-variant consensus accuracy (language=ALL)

          generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
         qwen/qwen3.7-max adversarial-length-locked  3            0.333333             0.916667 REVIEW
         qwen/qwen3.7-max adversarial-hard-negative  3            0.666667             0.666667   FAIL
         qwen/qwen3.7-max           taxonomy-guided  3            1.000000             0.750000   FAIL
         qwen/qwen3.7-max       overgenerate-select  3            0.666667             0.833333   FAIL
  google/gemini-2.5-flash adversarial-length-locked  3            0.666667             1.000000   FAIL
  google/gemini-2.5-flash adversarial-hard-negative  3            0.666667             1.000000   FAIL
  google/gemini-2.5-flash           taxonomy-guided  3            0.333333             0.750000 REVIEW
  google/gemini-2.5-flash       overgenerate-select  3            0.666667             0.916667   FAIL
anthropic/claude-sonnet-4           taxonomy-guided  3            0.333333             0.750000 REVIEW
anthropic/claude-sonnet-4       overgenerate-select  3            0.333333             0.750000 REVIEW
    google/gemma-4-31b-it adversarial-length-locked  3            0.666667             0.750000   FAIL
    google/gemma-4-31b-it adversarial-hard-negative  3            0.333333             0.916667 REVIEW

## Length-fallback deep dive

Total length_fallback items: 3 / 36 (8.3%)

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=68, B=47, C=47, D=40 (median=47)
  - A. (68 chars, 1.45x median) People must support their own families before helping the community.  **OUT OF ±35%**
  - B. (47 chars, 1.00x median) Opinion comes before the bravery of the braves.
  - C. (47 chars, 1.00x median) People in glass houses should not throw stones.
  - D. (40 chars, 0.85x median) The smarter you are, the less you speak.

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Option lengths: A=72, B=70, C=49, D=44 (median=60)
  - A. (72 chars, 1.21x median) The one whose hand is in fire is not like the one whose hand is in water
  - B. (70 chars, 1.18x median) One must provide for their family before donating to the local mosque.
  - C. (49 chars, 0.82x median) Older than you by a day, wiser than you by a year
  - D. (44 chars, 0.74x median) It is better to be alone than in bad company

### qwen_qwen3.7-max_adversarial-hard-negative_English_1
- Generator: qwen/qwen3.7-max | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
- Option lengths: A=46, B=56, C=37, D=61 (median=51)
  - A. (46 chars, 0.90x median) Overcoming adversity builds mental resilience.
  - B. (56 chars, 1.10x median) Have patience and endure whatever life may throw at you.
  - C. (37 chars, 0.73x median) Life includes hardship, not just fun.
  - D. (61 chars, 1.20x median) Experience is a more reliable source of knowledge than books.

## Partial items deep dive

Total partial items: 9 / 36

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. One should not donate to religious institutions if their family is in need.
  - B. It is important to take care of your own before helping others.
  - C. Knowing yourself is the beginning of all wisdom.
  - D. Family needs should be prioritized over community needs.

### google_gemma-4-31b-it_adversarial-hard-negative_English_1
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Everything is useful.
  - B. Adversity builds resilience.
  - C. Pain eliminates all weakness.
  - D. Survival guarantees improvement.

### google_gemini-2.5-flash_adversarial-hard-negative_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A stubborn person will eventually learn to follow instructions.
  - B. A difficult situation will teach one how to adapt and find a solution.
  - C. A poorly made tool will always cause problems for its user.
  - D. The person who fixes his eyes on the ground knows what he is looking for.

### anthropic_claude-sonnet-4_taxonomy-guided_English_1
- Generator: anthropic/claude-sonnet-4 | Variant: taxonomy-guided | Language: English
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
  - A. Retreating can preserve strength for future battles.
  - B. Taking calculated risks leads to personal growth and success.
  - C. Any challenge we face will automatically make us stronger.
  - D. Difficult experiences help us develop strength and resilience.

### qwen_qwen3.7-max_taxonomy-guided_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A difficult burden forces the carrier to discover a unique method for securing it safely on the journey.
  - B. An unusually shaped vessel demands that the farmer spend extra time preparing it before heading to market.
  - C. When the pawn has a fever, people say he is up to his usual tricks; when the owner is thus afflicted, they urge him to make an effort to eat.
  - D. A skilled farmer already knows the exact bindings required to secure every vessel brought in by the harvest.

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. Jump this way, jump that way is how a frog breaks its thigh. 
  - B. A challenging situation will eventually teach one the proper way to handle it.
  - C. A person's true character is revealed when faced with adversity.
  - D. Even a flawed tool can be made useful with enough effort.

### anthropic_claude-sonnet-4_taxonomy-guided_Yoruba_2
- Generator: anthropic/claude-sonnet-4 | Variant: taxonomy-guided | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A good pedigree is not something one can buy with money.
  - B. Those who carry heavy burdens must learn the proper way to balance them
  - C. When something doesn't work properly, it teaches us the right way to handle it
  - D. A gourd will always show the farmer how it should be tied

### anthropic_claude-sonnet-4_overgenerate-select_Arabic_0
- Generator: anthropic/claude-sonnet-4 | Variant: overgenerate-select | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Those who lack shelter should not judge places of worship.
  - B. Take care of your family's needs before helping others.
  - C. A person's true character is revealed in times of need.
  - D. Opinion comes before the bravery of the braves.

### anthropic_claude-sonnet-4_overgenerate-select_Yoruba_2
- Generator: anthropic/claude-sonnet-4 | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A vessel that breaks easily shows the potter where to strengthen the clay.
  - B. A burden that shifts constantly reveals which path the carrier should avoid.
  - C. One does not teach an elder that, what has been crushed should remain crushed.
  - D. A tool that causes discomfort will teach its user the proper way to handle it.

## Parse-fallback reasons

Total parse_fallback rows: 1

- **google/gemma-4-31b-it / adversarial-length-locked / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=['Charity begins at home', 'Faith requires action', 'Family values endure', 'Giving brings reward']

## High-consensus-wrong items

Count: 12 / 36 (33.3%)

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. People must support their own families before helping the community.
  - B. Opinion comes before the bravery of the braves.
  - C. People in glass houses should not throw stones.
  - D. The smarter you are, the less you speak.
- Correct label: A | Consensus: C (frac=1.00)

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A fragile calabash will eventually teach the harvester the gentle method to carry it safely.
  - B. A ripened calabash will eventually teach the harvester the perfect method to cut it cleanly.
  - C. A stubborn calabash will eventually teach the farmer the proper method to bind it securely.
  - D. A misshapen calabash will eventually teach the villager the creative method to carve it neatly.
- Correct label: C | Consensus: A (frac=0.75)

### google_gemma-4-31b-it_adversarial-length-locked_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A heavy harvest forces the farmer to build a stronger storage shed.
  - B. A cracked vessel shows the potter where the clay was most fragile.
  - C. A stubborn animal reveals the strength of the rope used to bind it.
  - D. A poorly fitting gourd teaches the farmer the best way to secure it.
- Correct label: D | Consensus: B (frac=0.75)

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: adversarial-length-locked | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A difficult situation will eventually teach one the proper way to handle it.
  - B. A farmer's wisdom is often revealed through the tools he chooses to use.
  - C. One must always adapt to the circumstances, even if they are uncomfortable.
  - D. The true measure of a person's skill is how they overcome unexpected challenges.
- Correct label: A | Consensus: D (frac=1.00)

### google_gemma-4-31b-it_adversarial-hard-negative_Arabic_0
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Give to the needy only after saving.
  - B. Support your community before yourself.
  - C. Prioritize your own family's needs first.
  - D. Balance home needs with public charity.
- Correct label: C | Consensus: D (frac=0.75)

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: adversarial-hard-negative | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. One should not donate to religious institutions if their family is in need.
  - B. It is important to take care of your own before helping others.
  - C. Knowing yourself is the beginning of all wisdom.
  - D. Family needs should be prioritized over community needs.
- Correct label: D | Consensus: B (frac=1.00)

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- Generator: google/gemma-4-31b-it | Variant: adversarial-hard-negative | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A gourd that doesn't fit comfortably will reveal to the farmer how to tie it properly.
  - B. The sort of stew you cooked and set the house on fire, you will explain.
  - C. The iron stake has been driven into the ground; the problem now is how to pull it out.
  - D. It is in the household that a featherless chicken is shunned; were it a partridge, humans would have killed it for food.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0
- Generator: google/gemini-2.5-flash | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. It is important to be generous and give to those in need.
  - B. Always ensure your home is in order before embarking on any major projects.
  - C. Giving to religious institutions is a highly commendable act of faith.
  - D. One should prioritize the needs of their own family before helping others.
- Correct label: D | Consensus: A (frac=0.75)

### anthropic_claude-sonnet-4_taxonomy-guided_Arabic_0
- Generator: anthropic/claude-sonnet-4 | Variant: taxonomy-guided | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Take care of your family's needs before helping others.
  - B. Religious duties should always come before personal matters.
  - C. Public service is more important than private concerns.
  - D. Helping others brings blessings to your own household.
- Correct label: A | Consensus: D (frac=0.75)

### anthropic_claude-sonnet-4_overgenerate-select_Arabic_0
- Generator: anthropic/claude-sonnet-4 | Variant: overgenerate-select | Language: Arabic
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
  - A. Those who lack shelter should not judge places of worship.
  - B. Take care of your family's needs before helping others.
  - C. A person's true character is revealed in times of need.
  - D. Opinion comes before the bravery of the braves.
- Correct label: B | Consensus: C (frac=1.00)

### qwen_qwen3.7-max_overgenerate-select_Yoruba_2
- Generator: qwen/qwen3.7-max | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. The experienced farmer relies on ancestral wisdom to bind every stubborn calabash.
  - B. An awkward calabash teaches the farmer the exact method required to secure it.
  - C. Villagers discard a misshapen calabash to seek a better vessel for the harvest.
  - D. A cracked calabash serves the farmer better as a grain scoop than a water vessel.
- Correct label: B | Consensus: D (frac=0.75)

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- Generator: google/gemini-2.5-flash | Variant: overgenerate-select | Language: Yoruba
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
  - A. A stubborn person will eventually yield to persistent effort.
  - B. One's true character is revealed through adversity and challenges.
  - C. A difficult task will teach one the proper method for its completion.
  - D. The tools one uses often dictate the quality of the work produced.
- Correct label: C | Consensus: B (frac=1.00)

## Distractor metrics

n_mcqs                            36.0000
avg_distractor_key_similarity      0.3120
std_distractor_key_similarity      0.1864
avg_pairwise_option_similarity     0.3408
std_pairwise_option_similarity     0.1732
option_length_mean                61.0000
option_length_cv                   0.3439
nli_replaced_total                 5.0000
duplicate_options_count            0.0000

## Yoruba curation samples

No curation metadata in this output.

## Root-cause synthesis

1. **Partial+fallback improved (47.2% → 36.1%).** The v62 length/leak relaxations worked: mean `fallback_count` dropped to 0.75, `length_replaced` is 0.00, and `length_fallback` fell to 8.3%.
2. **HCW and perfect consensus both got worse.** HCW rose from 25.0% to 33.3%; perfect consensus rose from 47.2% to 52.8%. The distractors are now attractive enough that auditors agree, but they often agree on the wrong answer (Arabic/Yoruba) or the correct answer is too obvious (English).
3. **English is still too easy.** 100% consensus correctness with 10 perfect-consensus items means distractors are not tempting enough.
4. **Arabic and Yoruba are broken in opposite ways.**
   - **Arabic:** only 41.7% consensus correct; 6/12 HCW. Many distractors are generic English idioms/proverbs (`People in glass houses...`, `The smarter you are...`, `Speech is silver...`, `The proof's in the pudding`) that the blocklist missed.
   - **Yoruba:** only 25.0% consensus correct; 6/12 HCW. The curated gold meaning is clearer, but distractors still cluster around the same gourd/farmer/bind concepts and several are themselves culturally generic proverbs.
5. **NLI filter is barely firing.** Only 5 NLI replacements across 36 items, yet several HCW distractors are clear paraphrases of the correct meaning. The embedding guard (0.55) may be suppressing legitimate NLI flags.
6. **Generator `google/gemma-4-31b-it` was benched** after a hard fallback and a parse fallback; `anthropic/claude-sonnet-4` was promoted. Active generator count stayed at 3, which is acceptable.
7. **Yoruba curation ran but metadata is not visible in `pilot1_test_generated_mcqs.csv`.** Raw outputs confirm the original literal gloss was rewritten to a more natural sentence, but the benefit is not showing in consensus accuracy yet.

## Options for v64

A. **Curate all gold meanings (English + Arabic + Yoruba).** Use the same cheap LLM path to rewrite every language's gloss into natural, non-idiomatic English. This should make English less clichéd and Arabic/Yoruba more precise.

B. **Tighten the generic-English idiom blocklist.** Add observed v63 leakages (`People in glass houses...`, `The smarter you are...`, `Speech is silver...`, `The proof's in the pudding`, `Opinion comes before the bravery...`, etc.) and consider fuzzy substring matching so partial variants are caught.

C. **Lower the NLI embedding guard for Arabic/Yoruba.** Drop `NLI_EMBEDDING_GUARD` from 0.55 to ~0.45 for non-English items so clear paraphrases are actually replaced instead of surviving as HCW items.

D. **Improve Yoruba curation prompt.** Instruct the curator to preserve key entities (`neckless gourd`, `farmer`, `tie/bind`) so the rewritten meaning stays semantically anchored and harder to confuse with near-paraphrase distractors.

E. **Add a post-generation difficulty rejection rule.** Discard or regenerate any item where a cheap single-auditor probe picks an answer with consensus_frac == 1.0. This directly targets perfect consensus but may reduce yield.

F. **Replace or de-prioritise the most brittle variant/generator pairs.** `adversarial-length-locked` produced 4 HCW items; `google/gemini-2.5-flash` produced 4 HCW items.

**Recommended v64 combination:** A + B + C + D. These address the two biggest drivers (generic-idiom shortcuts and paraphrase HCW) without adding a costly second audit loop. If perfect consensus stays high after that, add E.
