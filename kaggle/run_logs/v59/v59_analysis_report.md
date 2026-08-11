# v59 Kaggle Run Analysis

- Run timestamp: 2026-06-20T17:24:13.952074+00:00
- N_PER_LANG: 1
- Cost: $0.1886 / $5.00
- Active generators: ['openai/gpt-4.1-mini', 'google/gemini-2.5-pro', 'openai/gpt-4.1-nano']
- Benched generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash', 'anthropic/claude-sonnet-4']
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']

## Quality gates

| Gate | Value | Target | Pass |
|---|---|---|---|
| Consensus accuracy | 51.1% | - | - |
| Perfect consensus | 37.8% | <30% | ❌ |
| High-consensus-wrong | 28.9% | <10% (<15% stepping stone) | ❌ |
| Partial + fallback | 42.2% | <15% | ❌ |
| Duplicate options | 0 | 0 | ✅ |
| Key balance | {'A': 12, 'B': 11, 'C': 11, 'D': 11} | ~25% each | ✅ |

## Per-language consensus correctness

- Arabic: 46.7% (n=15)
- English: 80.0% (n=15)
- Yoruba: 26.7% (n=15)

## Generation status breakdown

generation_status
generated          26
partial             9
parse_fallback      8
length_fallback     2
Name: count, dtype: int64

## Per-generator/variant/language consensus accuracy

          generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
      openai/gpt-4.1-mini   adversarial-contrastive  1            0.000000             0.750000   PASS
      openai/gpt-4.1-mini       overgenerate-select  3            0.333333             0.583333 REVIEW
    google/gemini-2.5-pro   adversarial-contrastive  1            1.000000             1.000000   FAIL
    google/gemini-2.5-pro       overgenerate-select  3            0.333333             1.000000 REVIEW
      openai/gpt-4.1-nano   adversarial-contrastive  1            0.000000             0.750000   PASS
      openai/gpt-4.1-nano       overgenerate-select  3            0.333333             0.583333 REVIEW
         qwen/qwen3.7-max adversarial-length-locked  1            1.000000             1.000000   FAIL
    google/gemma-4-31b-it adversarial-length-locked  3            0.333333             0.833333 REVIEW
    google/gemma-4-31b-it adversarial-hard-negative  3            0.333333             0.833333 REVIEW
    google/gemma-4-31b-it           taxonomy-guided  3            0.000000             0.750000   PASS
    google/gemma-4-31b-it   adversarial-contrastive  2            0.500000             0.750000   FAIL
  google/gemini-2.5-flash adversarial-length-locked  3            0.666667             0.916667   FAIL
  google/gemini-2.5-flash adversarial-hard-negative  3            0.666667             0.750000   FAIL
  google/gemini-2.5-flash           taxonomy-guided  3            0.333333             1.000000 REVIEW
  google/gemini-2.5-flash   adversarial-contrastive  2            1.000000             0.750000   FAIL
anthropic/claude-sonnet-4 adversarial-length-locked  2            1.000000             0.625000   FAIL
anthropic/claude-sonnet-4 adversarial-hard-negative  3            0.666667             0.500000   FAIL
anthropic/claude-sonnet-4           taxonomy-guided  3            0.666667             0.666667   FAIL
anthropic/claude-sonnet-4   adversarial-contrastive  2            1.000000             0.750000   FAIL

## Parse fallback reasons

- **qwen/qwen3.7-max / adversarial-length-locked / Arabic**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['A person should provide for their family before giving to the community.', 'A person should save cash for their family before spending on charities.', 'A person should build walls for their house before giving to the shrine.', 'A person should teach morals to their kin before praying with the group.']
- **qwen/qwen3.7-max / adversarial-length-locked / Arabic**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['True generosity requires supporting your relatives before helping strangers.', 'True generosity requires funding the local mosque before helping strangers.', 'True generosity requires hoarding all your wealth inside your own house.', 'True generosity requires building public mosques to honor your relatives.']
- **anthropic/claude-sonnet-4 / adversarial-hard-negative / Arabic**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['One should prioritize family needs before helping others.', 'One should help neighbors before distant relatives.', 'One should give to the poor before the wealthy.', 'One should support local causes before global ones.']
- **google/gemma-4-31b-it / adversarial-contrastive / Arabic**
  - Options contain a generic English idiom/proverb that is not tied to this specific meaning. opts=['Charity begins at home', 'Charity begins with strangers', 'Charity begins only in crises', 'Charity begins through obligation']
- **google/gemini-2.5-flash / adversarial-contrastive / Arabic**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['Family needs should be prioritized over external obligations.', 'Community needs should be prioritized over personal obligations.', 'Personal needs should be prioritized over family obligations.', 'Financial needs should be prioritized over spiritual obligations.']
- **anthropic/claude-sonnet-4 / adversarial-contrastive / Arabic**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['One should take care of family needs before helping others.', 'One should help the community before addressing family needs.', 'Family members should take care of their own needs first.', 'One should always prioritize helping others over family needs.']
- **google/gemma-4-31b-it / adversarial-contrastive / English**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['Adversity builds resilience.', 'Comfort builds resilience.', 'Adversity builds strength only occasionally.', 'Resilience builds adversity.']
- **google/gemini-2.5-flash / adversarial-contrastive / English**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['Hardship develops fortitude.', 'Hardship reveals fortitude.', 'Hardship sometimes develops fortitude.', 'Hardship develops complacency.']
- **anthropic/claude-sonnet-4 / adversarial-contrastive / English**
  - Options contain a distractor that is a near-paraphrase or echo of the correct meaning. opts=['Adversity builds resilience.', 'Adversity builds character.', 'Success builds resilience.', 'Severe adversity builds resilience.']

## High-consensus-wrong items

### google_gemma-4-31b-it_adversarial-length-locked_Yoruba_2 (Yoruba, google/gemma-4-31b-it, adversarial-length-locked)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The broken basket will show the weaver how to mend it up.
  - B. The silent forest will show the hunter how to track it up.
  - C. The neckless gourd will show the farmer how to tie it up.
  - D. The empty granary will show the owner how to fill it up.
- Correct label: C | Consensus: D (frac=1.00)

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2 (Yoruba, google/gemini-2.5-flash, adversarial-length-locked)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. A person without proper guidance will inevitably struggle to find their place in the community, leading to their own downfall.
  - B. The wisdom of the elders is essential for guiding those who lack understanding, ensuring they are properly integrated into society.
  - C. One's true character is always revealed through their actions, regardless of their outward appearance or perceived weaknesses.
  - D. A person's inherent limitations will naturally reveal the appropriate way to handle them, guiding others on how to provide support.
- Correct label: D | Consensus: B (frac=0.75)

### google_gemma-4-31b-it_adversarial-hard-negative_Arabic_0 (Arabic, google/gemma-4-31b-it, adversarial-hard-negative)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Give to the community before your family.
  - B. Prioritize your own family's needs first.
  - C. Balance home needs with public charity.
  - D. Offer help to others once you are rich.
- Correct label: B | Consensus: C (frac=0.75)

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2 (Yoruba, google/gemma-4-31b-it, adversarial-hard-negative)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The farmer will discover the gourd's flaw while tying the knot.
  - B. A flawed gourd requires the farmer to invent a new way of tying.
  - C. The gourd's shape dictates the method the farmer uses to bind it.
  - D. The neckless gourd will show the farmer how it should be tied.
- Correct label: D | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0 (Arabic, google/gemini-2.5-flash, taxonomy-guided)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. It is important to be generous to your community.
  - B. One should always give to those less fortunate.
  - C. Religious institutions have a right to receive contributions.
  - D. Family needs should be prioritized over external donations.
- Correct label: D | Consensus: A (frac=1.00)

### google_gemma-4-31b-it_taxonomy-guided_English_1 (English, google/gemma-4-31b-it, taxonomy-guided)
- Proverb: That which does not kill us makes us stronger
- Correct meaning: Adversity builds resilience.
- Options:
  - A. The need for something forces people to find a way of obtaining it.
  - B. Overcoming hardships increases inner strength
  - C. Facing a challenge requires a brave mindset
  - D. Every difficult experience ensures future success
- Correct label: B | Consensus: A (frac=1.00)

### google_gemma-4-31b-it_taxonomy-guided_Yoruba_2 (Yoruba, google/gemma-4-31b-it, taxonomy-guided)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The flawed gourd reveals to the farmer the best way to secure it.
  - B. The farmer must learn the proper way to tie a gourd to avoid loss.
  - C. A skilled farmer knows how to handle every gourd in the harvest.
  - D. The gourd will remain loose unless the farmer uses a strong rope.
- Correct label: A | Consensus: B (frac=0.75)

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2 (Yoruba, google/gemini-2.5-flash, taxonomy-guided)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. One's true character is revealed through their actions, even without explicit instruction.
  - B. A person lacking guidance will eventually reveal their true nature and needs.
  - C. Even without a clear path, a determined individual will find a way to achieve their goals.
  - D. A person's inherent limitations will always dictate their ultimate destiny.
- Correct label: B | Consensus: A (frac=1.00)

### google_gemma-4-31b-it_adversarial-contrastive_Arabic_0 (Arabic, google/gemma-4-31b-it, adversarial-contrastive)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A.  Rome wasn't built in a day.
  - B. Preaching to the choir.
  - C. I dug my own grave.
  - D. Charity begins at home.
- Correct label: D | Consensus: A (frac=1.00)

### openai_gpt-4.1-mini_adversarial-contrastive_Yoruba_2 (Yoruba, openai/gpt-4.1-mini, adversarial-contrastive)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The farmer will decide how to tie the gourd only after it has fully grown.
  - B. The gourd without a neck will show the farmer the best way to secure it.
  - C. Only when the gourd is harvested will the farmer know how to handle it.
  - D. The way the gourd is tied depends on the advice of the elders, not the gourd itself.
- Correct label: B | Consensus: A (frac=0.75)

### openai_gpt-4.1-nano_adversarial-contrastive_Yoruba_2 (Yoruba, openai/gpt-4.1-nano, adversarial-contrastive)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The farmer's skill in tying gourds depends on the gourd’s own shape.
  - B. The farmer’s success in farming depends on the gourd’s appearance.
  - C. The gourd will show the farmer how to harvest it without help.
  - D. The farmer will understand how to tie the gourd by observing it himself.
- Correct label: D | Consensus: A (frac=0.75)

### google_gemini-2.5-pro_overgenerate-select_Arabic_0 (Arabic, google/gemini-2.5-pro, overgenerate-select)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Sacred duties must always take precedence.
  - B. Your first duty is to your own family.
  - C. A Jack of all trades is master of none.
  - D. Balance your duties to family and community.
- Correct label: B | Consensus: D (frac=1.00)

### google_gemini-2.5-pro_overgenerate-select_Yoruba_2 (Yoruba, google/gemini-2.5-pro, overgenerate-select)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. A person with a fundamental character flaw cannot be easily corrected.
  - B. A wise person can make use of even flawed or incomplete things.
  - C. A difficult matter should be presented to elders for their wisdom.
  - D. An unusual problem will itself suggest the proper way to approach it.
- Correct label: D | Consensus: B (frac=1.00)

## Distractor metrics

n_mcqs                            45.0000
avg_distractor_key_similarity      0.3233
std_distractor_key_similarity      0.2407
avg_pairwise_option_similarity     0.3503
std_pairwise_option_similarity     0.2083
option_length_mean                52.8000
option_length_cv                   0.4324
nli_replaced_total                 9.0000
duplicate_options_count            0.0000

## Root-cause summary

1. All three generator starters (`qwen/qwen3.7-max`, `google/gemma-4-31b-it`, `google/gemini-2.5-flash`) and the Anthropic substitute were benched after 2 `parse_fallback` failures each.
2. The remaining active roster (`openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `google/gemini-2.5-pro`) is cheaper but produced lower-quality distractors, driving high-consensus-wrong up to 28.9%.
3. `has_correct_meaning_leak()` is rejecting entire option sets for near-paraphrases rather than replacing the leaking distractor, causing the parse-fallback avalanche and benching.
4. Partial+fallback is 42.2%, far above the 15% target, because the semantic/NLI/length sanitizers are replacing many distractors and the leak filter is throwing away otherwise usable generations.
5. Yoruba consensus correctness collapsed to 26.7% (from 40.0% in v58) after the starter generators were benched.

## Recommended next step (v60)

- Convert `has_correct_meaning_leak()` from a hard parse-fallback into a **sanitizer** that replaces the leaking distractor(s) with fallback samples, preserving the generator call.
- Raise the generator soft-failure threshold (or do not bench for soft parse/meta/idiom failures) so high-quality starters are not lost after only 2 quality-filter rejections.
- Re-run N=1 on Kaggle and re-check the gates. If partial+fallback remains high, relax the semantic-distance band or NLI embedding guard.
