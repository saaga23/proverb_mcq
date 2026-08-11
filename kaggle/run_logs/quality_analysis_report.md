# Kaggle Kernel v58 Quality Analysis Report

**Run timestamp:** 2026-06-20T13:59:26.407515+00:00
**Seed:** 20260615 | **N_PER_LANG:** 1 | **Cost:** $0.2237 / $5.00

## Executive Summary vs Publication Gates

| Gate | Target | Actual | Status |
|---|---|---|---|
| Hard fallback rate | <5% | 24.4% (11/45) | FAIL |
| Partial + fallback rate | <15% | 28.9% (13/45) | FAIL |
| Active generators / auditors | ≥3 each | gen=3, aud=4 | PASS |
| Perfect consensus rate | <30% | 48.9% (22/45) | FAIL |
| High-consensus-wrong rate | <10% | 22.2% (10/45) | FAIL |
| Overall consensus accuracy | — | 60.0% | — |
| Arabic consensus accuracy | ≥50% | 53.3% | PASS |
| English consensus accuracy | ≥50% | 86.7% | PASS |
| Yoruba consensus accuracy | ≥50% | 40.0% | FAIL |
| Duplicate options | 0% | 2 | FAIL |
| Correct-key balance | ~25% each | A=26.7% B=24.4% C=24.4% D=24.4% | PASS |

## Baseline Comparison (N=2 before fixes)

| Metric | Before fixes | v58 after fixes | Δ |
|---|---|---|---|
| Perfect consensus | 41.1% | 48.9% | +7.8% |
| High-consensus-wrong | 27.2% | 22.2% | -5.0% |
| Consensus accuracy | 55.0% | 60.0% | +5.0% |
| Yoruba accuracy | 40.0% | 40.0% | +0.0% |
| Partial+fallback | 19.4% | 28.9% | +9.5% |

## Generation Status Breakdown

- **generated**: 32 (71.1%)
- **length_fallback**: 7 (15.6%)
- **partial**: 4 (8.9%)
- **parse_fallback**: 2 (4.4%)

## Per-Language Consensus Accuracy

| Language | N | Accuracy |
|---|---|---|
| Arabic | 15 | 53.3% |
| English | 15 | 86.7% |
| Yoruba | 15 | 40.0% |

## Per-Generator Consensus Accuracy

| Generator | N | Accuracy |
|---|---|---|
| google/gemini-2.5-flash | 15 | 66.7% |
| google/gemma-4-31b-it | 15 | 53.3% |
| qwen/qwen3.7-max | 15 | 60.0% |

## Per-Variant Consensus Accuracy

| Variant | N | Accuracy |
|---|---|---|
| adversarial-contrastive | 9 | 55.6% |
| adversarial-hard-negative | 9 | 55.6% |
| adversarial-length-locked | 9 | 77.8% |
| overgenerate-select | 9 | 55.6% |
| taxonomy-guided | 9 | 55.6% |

## High-Consensus-Wrong Items (≥0.75 consensus, wrong)

*10 items (22.2%)*


### google_gemini-2.5-flash_overgenerate-select_Arabic_0
- **Generator:** google/gemini-2.5-flash | **Variant:** overgenerate-select | **Language:** Arabic | **Status:** generated | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** C | **Consensus:** D (frac=0.75)
  - **A:** Religious institutions should not interfere with domestic affairs.
  - **B:** What is needed at home should not be taken to the mosque.
  - **C ✅:** One should prioritize their family's needs before helping others.
  - **D:** Generosity should extend beyond one's immediate surroundings.

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0
- **Generator:** google/gemini-2.5-flash | **Variant:** taxonomy-guided | **Language:** Arabic | **Status:** generated | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** A | **Consensus:** B (frac=0.75)
  - **A ✅:** Family needs should be prioritized over external donations.
  - **B:** It is important to be generous to your community.
  - **C:** One should always give to those less fortunate.
  - **D:** Religious institutions have a right to receive contributions.

### google_gemma-4-31b-it_adversarial-length-locked_Arabic_0
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-length-locked | **Language:** Arabic | **Status:** generated | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** B | **Consensus:** A (frac=0.75)
  - **A:** Offer your help to the community.
  - **B ✅:** Prioritize your family's needs first.
  - **C:** Keep your private life very secret.
  - **D:** Follow the rules of the local house.

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0
- **Generator:** google/gemma-4-31b-it | **Variant:** taxonomy-guided | **Language:** Arabic | **Status:** generated | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** D | **Consensus:** A (frac=0.75)
  - **A:** Give your extra resources to the local community center.
  - **B:** Support the needy in your city to earn spiritual merit.
  - **C:** Donate everything you own to the mosque for a blessing.
  - **D ✅:** Prioritize your own family's needs before helping others.

### qwen_qwen3.7-max_taxonomy-guided_Arabic_0
- **Generator:** qwen/qwen3.7-max | **Variant:** taxonomy-guided | **Language:** Arabic | **Status:** generated | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** C | **Consensus:** A (frac=0.75)
  - **A:** Families require adequate resources to maintain their daily household needs.
  - **B:** Citizens ought to fund local neighborhood projects before national campaigns.
  - **C ✅:** People should support their own relatives before giving to outside causes.
  - **D:** Families should always prioritize their own desires over community obligations.

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2
- **Generator:** google/gemini-2.5-flash | **Variant:** overgenerate-select | **Language:** Yoruba | **Status:** generated | **Fallbacks:** 0
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** A | **Consensus:** C (frac=1.00)
  - **A ✅:** The object itself will reveal the proper way it should be handled or utilized.
  - **B:** A person's inherent limitations will dictate the assistance they require from others.
  - **C:** One's true nature is revealed through the challenges they face, not by their outward appearance.
  - **D:** The wise farmer understands that some tasks require unconventional methods.

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2
- **Generator:** google/gemini-2.5-flash | **Variant:** taxonomy-guided | **Language:** Yoruba | **Status:** generated | **Fallbacks:** 0
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** C | **Consensus:** A (frac=1.00)
  - **A:** One's true character is revealed through their actions, even without explicit instruction.
  - **B:** Even without a clear path, a determined individual will find a way to achieve their goals.
  - **C ✅:** A person lacking guidance will eventually reveal their true nature and needs.
  - **D:** A person's inherent limitations will always dictate their ultimate destiny.

### google_gemma-4-31b-it_adversarial-contrastive_Yoruba_2
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-contrastive | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 5
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** C | **Consensus:** D (frac=1.00)
  - **A:** One does not see leaves lying about and scoop up feces with one’s bare hand.
  - **B:** The cockroach overreaches itself when it says it will dance in the company of chick ens.
  - **C ✅:** The neckless gourd will itself indicate to the farmer how to tie it up.
  - **D:** The road will eventually expose the thief; the farm hut will eventually expose the farmer.

### qwen_qwen3.7-max_adversarial-contrastive_Yoruba_2
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-contrastive | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 3
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** B | **Consensus:** A (frac=1.00)
  - **A:** A ladder rests on the ground and leans on the house; if the person one leans on must remove his support, he should give warning.
  - **B ✅:** A person with unusual traits will naturally show the community the specific way they must be managed.
  - **C:** A person with unusual traits will naturally compel the village to exile them for being hard to manage.
  - **D:** Kin acknowledges only the rich; no kin claims a poverty-ridden person; the way farer who has no money for kin rips up his papers.

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-hard-negative | **Language:** Yoruba | **Status:** generated | **Fallbacks:** 0
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** D | **Consensus:** A (frac=0.75)
  - **A:** An observant elder will eventually discover the hidden method required to manage a stubborn youth.
  - **B:** A stubborn person will eventually force the local community to invent a new method of discipline.
  - **C:** A person lacking proper guidance will eventually learn to adapt to the strict rules of the village.
  - **D ✅:** A person with an unusual nature will eventually reveal to others exactly how they must be handled.

## Non-Generated (Partial / Fallback) Items

*13 items (28.9%)*


### google_gemma-4-31b-it_adversarial-contrastive_Arabic_0
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-contrastive | **Language:** Arabic | **Status:** parse_fallback | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** A
  - **A:** Charity begins at home.
  - **B:** Go big or go home.
  - **C:** East or west, home is the best
  - **D:** A lion at home, a lamb abroad.

### google_gemma-4-31b-it_overgenerate-select_Arabic_0
- **Generator:** google/gemma-4-31b-it | **Variant:** overgenerate-select | **Language:** Arabic | **Status:** parse_fallback | **Fallbacks:** 0
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** B
  - **A:** Defend your home.
  - **B:** Charity begins at home.
  - **C:** East or west, home is best 
  - **D:** Go big or go home.

### qwen_qwen3.7-max_adversarial-contrastive_Arabic_0
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-contrastive | **Language:** Arabic | **Status:** partial | **Fallbacks:** 2
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** D
  - **A:** Acts of charity should begin with one's close friends.
  - **B:** Acts of charity should begin during times of hardship.
  - **C:** East or west, home is best 
  - **D:** Acts of charity should begin within one's own home.

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-length-locked | **Language:** Arabic | **Status:** partial | **Fallbacks:** 2
- **Proverb:** اللي يعوزه البيت يحرم على الجامع
- **Correct meaning:** Charity begins at home. | **Correct key:** A
  - **A:** People must provide for their own families before helping the public.
  - **B:** People must donate to their local temples before supporting the public.
  - **C:** People must store wealth for their own houses before helping the public.
  - **D:** Make a rod for one’s own back.

### google_gemini-2.5-flash_adversarial-contrastive_English_1
- **Generator:** google/gemini-2.5-flash | **Variant:** adversarial-contrastive | **Language:** English | **Status:** length_fallback | **Fallbacks:** 3
- **Proverb:** That which does not kill us makes us stronger
- **Correct meaning:** Adversity builds resilience. | **Correct key:** A
  - **A:** Hardship develops fortitude.
  - **B:** Everyone experiences hardship.
  - **C:** Everyone experiences hardship.
  - **D:** Hardship develops complacency.

### google_gemini-2.5-flash_adversarial-length-locked_English_1
- **Generator:** google/gemini-2.5-flash | **Variant:** adversarial-length-locked | **Language:** English | **Status:** partial | **Fallbacks:** 2
- **Proverb:** That which does not kill us makes us stronger
- **Correct meaning:** Adversity builds resilience. | **Correct key:** B
  - **A:** Difficult experiences inevitably lead to greater physical strength.
  - **B:** Challenges contribute to personal growth and fortitude.
  - **C:** Food has a profound impact on your physical and personal growth, so be thoughtful with what you eat.
  - **D:** Suffering is a necessary component of all human achievement.

### google_gemma-4-31b-it_adversarial-contrastive_English_1
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-contrastive | **Language:** English | **Status:** length_fallback | **Fallbacks:** 3
- **Proverb:** That which does not kill us makes us stronger
- **Correct meaning:** Adversity builds resilience. | **Correct key:** D
  - **A:** Comfort builds resilience.
  - **B:** Stay positive in adversity.
  - **C:** Stay positive in adversity.
  - **D:** Adversity builds resilience.

### qwen_qwen3.7-max_adversarial-contrastive_English_1
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-contrastive | **Language:** English | **Status:** length_fallback | **Fallbacks:** 6
- **Proverb:** That which does not kill us makes us stronger
- **Correct meaning:** Adversity builds resilience. | **Correct key:** C
  - **A:** Build new relationships while maintaining existing ones.
  - **B:** Adversity builds resilience.
  - **C:** Hardships build inner resilience.
  - **D:** Love will overcome hardships or interference from others.

### google_gemini-2.5-flash_adversarial-contrastive_Yoruba_2
- **Generator:** google/gemini-2.5-flash | **Variant:** adversarial-contrastive | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 3
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** D
  - **A:** Firmly planted and unshakable is the way one finds the city fortification.
  - **B:** A person's inherent strengths will reveal the appropriate way to handle them.
  - **C:** Hunger affects people the same way, but disasters do not hurt people the same way.
  - **D:** A person's inherent limitations will reveal the appropriate way to handle them.

### google_gemma-4-31b-it_adversarial-contrastive_Yoruba_2
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-contrastive | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 5
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** C
  - **A:** One does not see leaves lying about and scoop up feces with one’s bare hand.
  - **B:** The cockroach overreaches itself when it says it will dance in the company of chick ens.
  - **C:** The neckless gourd will itself indicate to the farmer how to tie it up.
  - **D:** The road will eventually expose the thief; the farm hut will eventually expose the farmer.

### google_gemma-4-31b-it_adversarial-hard-negative_Yoruba_2
- **Generator:** google/gemma-4-31b-it | **Variant:** adversarial-hard-negative | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 4
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** A
  - **A:** The neckless gourd will itself indicate to the farmer how to tie it up.
  - **B:** It is by its flight that the parrot proves itself a formidable bird.
  - **C:** Whatever bird emulates the vulture will find itself behind the cooking hearth. F
  - **D:** Do not lay down the law; the law will lay itself down.

### qwen_qwen3.7-max_adversarial-contrastive_Yoruba_2
- **Generator:** qwen/qwen3.7-max | **Variant:** adversarial-contrastive | **Language:** Yoruba | **Status:** length_fallback | **Fallbacks:** 3
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** B
  - **A:** A ladder rests on the ground and leans on the house; if the person one leans on must remove his support, he should give warning.
  - **B:** A person with unusual traits will naturally show the community the specific way they must be managed.
  - **C:** A person with unusual traits will naturally compel the village to exile them for being hard to manage.
  - **D:** Kin acknowledges only the rich; no kin claims a poverty-ridden person; the way farer who has no money for kin rips up his papers.

### qwen_qwen3.7-max_overgenerate-select_Yoruba_2
- **Generator:** qwen/qwen3.7-max | **Variant:** overgenerate-select | **Language:** Yoruba | **Status:** partial | **Fallbacks:** 2
- **Proverb:** Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- **Correct meaning:** The neckless gourd will itself indicate to the farmer how to tie it up. | **Correct key:** C
  - **A:** A wise elder must patiently instruct the novice on the proper way to bind the harvest.
  - **B:** Initiates of mysteries must rally round other initiates; if initiates do not rally round one another, they suffer disgrace.
  - **C:** Someone with a peculiar disposition will naturally reveal how they must be handled.
  - **D:** Wayward youth require the tightest ropes and the firmest hands to keep them in order.

## Duplicate Options

*2 MCQs flagged with duplicate options.*


- **google_gemma-4-31b-it_adversarial-contrastive_English_1** (google/gemma-4-31b-it / adversarial-contrastive / English)
  - **A:** Comfort builds resilience.
  - **B:** Stay positive in adversity.
  - **C:** Stay positive in adversity.
  - **D:** Adversity builds resilience.

- **google_gemini-2.5-flash_adversarial-contrastive_English_1** (google/gemini-2.5-flash / adversarial-contrastive / English)
  - **A:** Hardship develops fortitude.
  - **B:** Everyone experiences hardship.
  - **C:** Everyone experiences hardship.
  - **D:** Hardship develops complacency.

## Audit Committee Metrics

- **meta-llama/llama-3.3-70b-instruct** hit rate: 57.8%
- **mistralai/mistral-small-3.2-24b-instruct** hit rate: 55.6%
- **google/gemma-3-27b-it** hit rate: 66.7%
- **deepseek/deepseek-v3.2** hit rate: 62.2%

## Interpretation & Recommendations

1. **The fixes did not yet move the gates to publication-ready levels.**
   - Perfect consensus actually *increased* from 41.1% → 48.9%.
   - High-consensus-wrong dropped only modestly from 27.2% → 22.2%.
   - Partial+fallback rate worsened from 19.4% → 28.9%.
   - Yoruba remained at 40.0%, below the ≥50% gate.

2. **The most urgent problem is still confident-but-wrong consensus.**
   - 10/45 items show strong auditor agreement on the wrong answer.
   - This is the signature of surface shortcuts (antonyms, length, generic idioms) that survive the current filters.

3. **Partial/fallback rate is too high.**
   - 7 length_fallback + 4 partial + 2 parse_fallback out of 45 items.
   - Suggests the new semantic-distance band and length/overlap filters are rejecting too many model outputs.

4. **Duplicates appeared.**
   - 2 MCQs contain duplicate options; the de-duplication/post-processor needs tightening.

5. **Recommended next iteration:**
   - Tighten prompt instructions to avoid generating generic English proverbs (e.g. 'Charity begins at home' leaks into Arabic/English options).
   - Add an explicit 'no antonym of the correct meaning' rule and a lexical overlap check against the correct meaning.
   - Relax the length fallback threshold slightly while keeping >2× ban, to reduce length_fallback without reintroducing obvious length shortcuts.
   - Add a second-pass auditor disagreement trigger: items with consensus_frac≥0.75 but low inter-auditor hit diversity should be flagged for human review.
   - For Yoruba, test a language-specific semantic band and a blocklist of commonly leaked English glosses.
