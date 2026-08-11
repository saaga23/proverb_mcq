# v65 Forensic Deep Dive

## 1. Generation-status composition

generation_status
generated          22
partial             9
length_fallback     4
hard_fallback       1
Name: count, dtype: int64

| Status | Count | Share |
|---|---|---|
| generated | 22 | 61.1% |
| partial | 9 | 25.0% |
| length_fallback | 4 | 11.1% |
| hard_fallback | 1 | 2.8% |

## 2. English items: why consensus is 100% correct

English distractors are overwhelmingly generic reversals or unrelated statements. Auditors can pick the key without hesitation.

### google_gemma-4-31b-it_adversarial-hard-negative_English_1 | status=generated | consensus_frac=1.0
- Correct label: B | Consensus: B
- **A.** Surviving a crisis ensures that we will never be hurt again.
- **B.** Facing hardships helps us become more resilient and capable.
- **C.** Enduring pain automatically increases our physical strength.
- **D.** Overcoming a struggle proves that we are superior to others.

### google_gemini-2.5-flash_adversarial-hard-negative_English_1 | status=generated | consensus_frac=1.0
- Correct label: C | Consensus: C
- **A.** Avoiding difficult situations prevents us from experiencing personal development.
- **B.** Overcoming obstacles is a sign of inherent strength, not a cause of it.
- **C.** Adversity and challenges contribute to our growth and fortitude.
- **D.** Only life-threatening experiences truly build character and resolve.

### google_gemma-4-31b-it_adversarial-length-locked_English_1 | status=generated | consensus_frac=1.0
- Correct label: A | Consensus: A
- **A.** Facing hardships helps us become more resilient and capable.
- **B.** Enduring pain ensures that we avoid future physical injuries.
- **C.** Surviving a crisis proves that we are naturally superior.
- **D.** Overcoming a struggle means we have reached our peak limit.

### google_gemini-2.5-flash_adversarial-length-locked_English_1 | status=generated | consensus_frac=1.0
- Correct label: B | Consensus: B
- **A.** Avoiding difficult situations ensures a peaceful and untroubled existence.
- **B.** Adversity builds character and increases our ability to cope with future challenges.
- **C.** Overcoming minor obstacles leads to a sense of temporary accomplishment.
- **D.** Life's struggles are best ignored to maintain a positive outlook.

### qwen_qwen3.7-max_overgenerate-select_English_1 | status=generated | consensus_frac=1.0
- Correct label: C | Consensus: C
- **A.** A careful avoidance of lethal dangers ensures a longer, healthier lifespan.
- **B.** Individuals who engage in brutal combat develop superior physical power.
- **C.** Severe adversity builds enduring personal resilience and inner fortitude.
- **D.** Survivors of fatal blows often gain complete immunity against future harm.

### google_gemini-2.5-flash_overgenerate-select_English_1 | status=generated | consensus_frac=1.0
- Correct label: D | Consensus: D
- **A.** Avoiding danger is the surest path to a long and healthy life.
- **B.** Only through extreme suffering can one truly understand their own limits.
- **C.** Survival is the ultimate measure of one's inherent strength and resilience.
- **D.** Adversity and challenges contribute to personal growth and increased fortitude.

### google_gemma-4-31b-it_taxonomy-guided_English_1 | status=generated | consensus_frac=0.5
- Correct label: C | Consensus: C
- **A.** Surviving a dangerous event is a sign of great power.
- **B.** Consistent practice leads to mastery of a new skill.
- **C.** Overcoming difficult challenges increases our inner strength.
- **D.** Every experience in life contributes to personal growth.

### google_gemini-2.5-flash_taxonomy-guided_English_1 | status=generated | consensus_frac=1.0
- Correct label: D | Consensus: D
- **A.** Surviving difficult experiences means we are more powerful than before.
- **B.** Avoiding danger is the best way to ensure a long and healthy life.
- **C.** Any experience, regardless of its nature, inevitably leads to personal improvement.
- **D.** Adversity and challenges contribute to our growth and fortitude.

### qwen_qwen3.7-max_adversarial-hard-negative_English_1 | status=partial | consensus_frac=1.0
- Correct label: A | Consensus: A
- **A.** Enduring severe hardships ultimately helps us become more resilient and capable.
- **B.** Sometimes you can trust an enemy more than an alleged friend.
- **C.** One positive action can have a long -lasting impact.
- **D.** Enduring minor inconveniences ultimately helps us become more resilient and capable.

### qwen_qwen3.7-max_adversarial-length-locked_English_1 | status=partial | consensus_frac=1.0
- Correct label: D | Consensus: D
- **A.** Different people have different taste s, so what one person loves might be terrible to another.
- **B.** Studying past failures helps scholars to gain deeper intellectual insight and theoretical knowledge.
- **C.** Surviving market crashes enables investors to secure larger financial wealth and material prosperity.
- **D.** Enduring tough trials allows people to build greater emotional resilience and practical competence.

### anthropic_claude-sonnet-4_overgenerate-select_English_1 | status=partial | consensus_frac=0.5
- Correct label: A | Consensus: A
- **A.** Facing hardships helps us become more resilient and capable.
- **B.** Surviving dangerous situations teaches us to avoid similar risks in the future.
- **C.** Overcoming challenges reveals our hidden talents and natural abilities.
- **D.** People are most tempted by that which is tab oo or prohibited.

### qwen_qwen3.7-max_taxonomy-guided_English_1 | status=partial | consensus_frac=0.5
- Correct label: B | Consensus: B
- **A.** The effects on the greater whole are visible in each of its parts.
- **B.** Enduring severe adversity ultimately builds greater psychological resilience and fortitude.
- **C.** Enduring physical exertion ultimately builds greater muscular endurance and physical vitality.
- **D.** If you are having a difficult time now, maintain your hope that you will have success later.

## 3. Yoruba HCW / low-correctness items

Yoruba distractors are either (a) structurally parallel analogies that auditors prefer, or (b) abstract truisms that are more coherent than the concrete gourd/farmer meaning.

### qwen_qwen3.7-max_adversarial-length-locked_Yoruba_2 | status=generated | consensus_frac=0.75
- Correct label: C | Consensus: D
- **A.** A heavily cracked clay pot shows the potter the proper way to fire it in the village kiln.
- **B.** A remarkably heavy yam crop shows the elder the safest way to store it in the wooden barn.
- **C.** A uniquely shaped calabash shows the harvester the exact way to bind it for the journey.
- **D.** A severely dull iron blade shows the smith the precise way to sharpen it on the stone.

### google_gemini-2.5-flash_adversarial-length-locked_Yoruba_2 | status=generated | consensus_frac=1.0
- Correct label: A | Consensus: C
- **A.** A challenging situation will reveal the best way to handle it, teaching resourcefulness.
- **B.** A person without proper guidance will struggle to find their place in the community.
- **C.** One's true character is often revealed when faced with unexpected difficulties.
- **D.** The wisdom of the elders is essential for navigating life's complex problems.

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2 | status=generated | consensus_frac=1.0
- Correct label: C | Consensus: B
- **A.** A stubborn person will eventually yield to a stronger will.
- **B.** One's true character is revealed in times of adversity.
- **C.** A challenging situation will reveal the best approach to overcome it.
- **D.** The most difficult tasks often require the simplest solutions.

## 4. Arabic HCW / generic-idiom leakage

Arabic items still contain generic English idioms as distractors (e.g., "A living dog is better than a dead lion", "He who gathers honey..."). These are easy to rule out, but some plausible community-focused distractors attract consensus.

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0 | status=length_fallback | correct=0 | consensus_frac=0.25
- **A.** A person must support their own family before giving charity to the public. ✅
- **B.** Beware the levelheaded person if they’re angry.
- **C.** The best answer will come from the person who is not angry.
- **D.** He who gathers honey, must suffer the stings

### google_gemma-4-31b-it_adversarial-length-locked_Arabic_0 | status=generated | correct=1 | consensus_frac=0.75
- **A.** Give your largest donations to the local community center.
- **B.** Prioritize your own family's needs before helping others. ✅
- **C.** Build a strong house before visiting the city temple.
- **D.** Share all your wealth with the poor in your neighborhood.

### google_gemini-2.5-flash_adversarial-length-locked_Arabic_0 | status=partial | correct=1 | consensus_frac=0.5
- **A.** It’s better to avoid mistakes altogether than do something that you should apologize for after.
- **B.** It is important to prioritize community needs over individual family desires.
- **C.** One's primary responsibility is to their household before assisting those outside of it. ✅
- **D.** Always ensure your own needs are met before considering the needs of others.

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0 | status=length_fallback | correct=1 | consensus_frac=0.75
- **A.** I curse my own child but I hate whoever says “amen.”
- **B.** One must provide for their own household before giving charity to the public. ✅
- **C.** One should prioritize building a solid home over engaging in public worship.
- **D.** Don't sell the skin before you've caught the bear.

### google_gemma-4-31b-it_adversarial-hard-negative_Arabic_0 | status=generated | correct=1 | consensus_frac=1.0
- **A.** Prioritize charitable giving over the needs of your family.
- **B.** Ensure your family is wealthy before donating to the needy.
- **C.** Prioritize the needs of your own family before helping others. ✅
- **D.** Help those in your community before focusing on your family.

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0 | status=length_fallback | correct=0 | consensus_frac=0.5
- **A.**  A living dog is better than a dead lion.
- **B.** The world is like a belly-dancer: it dances a little while for everyone
- **C.** You should only help others if your family has no needs at all.
- **D.** One should prioritize their family's needs over external charitable acts. ✅

### qwen_qwen3.7-max_taxonomy-guided_Arabic_0 | status=generated | correct=1 | consensus_frac=1.0
- **A.** Donating valuable resources to religious institutions is strictly prohibited when a person has limited wealth.
- **B.** Employees must secure their own financial stability before volunteering time to corporate social programs.
- **C.** Individuals must prioritize providing for their own household before giving charity to the wider community. ✅
- **D.** Households are expected to divide their surplus income equally between domestic expenses and public charities.

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0 | status=partial | correct=0 | consensus_frac=0.5
- **A.** Choose a partner/ friend before choosing a path.
- **B.** Give generously to the community to ensure a blessing.
- **C.** Donate everything you have to the mosque for reward.
- **D.** Prioritize your own family's needs before helping others. ✅

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0 | status=generated | correct=0 | consensus_frac=1.0
- **A.** One should prioritize their immediate family's needs before extending assistance to the wider community. ✅
- **B.** It is important to contribute to your local community whenever possible.
- **C.** The best answer will come from the person who is not angry.
- **D.** Helping others is a noble act, regardless of your personal circumstances.

### qwen_qwen3.7-max_overgenerate-select_Arabic_0 | status=generated | correct=0 | consensus_frac=0.5
- **A.** Fulfilling religious obligations must always take precedence over household needs.
- **B.** People often display public piety while neglecting their private duties at home.
- **C.** Resources gathered for public institutions must never be used for private gain.
- **D.** Caring for your immediate family takes priority over donating to public causes. ✅

### google_gemma-4-31b-it_overgenerate-select_Arabic_0 | status=hard_fallback | correct=1 | consensus_frac=0.75
- **A.** A person should take care of their own family before offering help to others. ✅
- **B.** Climbing the ladder of success by stepping on others.
- **C.** A person of two minds is a liar, and a person of three minds is a hypocrite
- **D.** Don't sell the skin before you've caught the bear.

### google_gemini-2.5-flash_overgenerate-select_Arabic_0 | status=generated | correct=0 | consensus_frac=0.5
- **A.** One should always give to the community before personal gain.
- **B.** Charity begins at home, so prioritize your family's needs. ✅
- **C.** It is important to share your wealth with those less fortunate.
- **D.** Focus on your spiritual duties before worldly responsibilities.

## 5. Length-fallback items: raw model outputs vs final options

### qwen_qwen3.7-max_adversarial-length-locked_Arabic_0
- Correct meaning: Charity begins at home.
- Final options:
  - A. A person must support their own family before giving charity to the public. (75 chars)
  - B. Beware the levelheaded person if they’re angry. (47 chars)
  - C. The best answer will come from the person who is not angry. (59 chars)
  - D. He who gathers honey, must suffer the stings (44 chars)
- Raw model output:
  ```[
  "A person must prioritize giving support to their family before donating money to the community.",
  "A person must prioritize offering prayers to their mosque before giving support to their family.",
  "A person must prioritize saving wealth for their future before investing capital in the market.",
  "A person must prioritize repairing damage to their house before building structures for the town."
]```

### qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0
- Correct meaning: Charity begins at home.
- Final options:
  - A. I curse my own child but I hate whoever says “amen.” (52 chars)
  - B. One must provide for their own household before giving charity to the public. (77 chars)
  - C. One should prioritize building a solid home over engaging in public worship. (76 chars)
  - D. Don't sell the skin before you've caught the bear. (50 chars)
- Raw model output:
  ```["One must provide for their own household before giving charity to the public.", "One must secure their own household's wealth before donating to the community.", "One should prioritize building a solid home over engaging in public worship.", "One must prioritize their family's luxuries over the basic needs of others."]```

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0
- Correct meaning: Charity begins at home.
- Final options:
  - A.  A living dog is better than a dead lion. (41 chars)
  - B. The world is like a belly-dancer: it dances a little while for everyone (71 chars)
  - C. You should only help others if your family has no needs at all. (63 chars)
  - D. One should prioritize their family's needs over external charitable acts. (73 chars)
- Raw model output:
  ```["One should prioritize their family's needs over external charitable acts.", "Charity begins at home, but should not end there.", "It is important to ensure your family is well-provided for before helping others.", "You should only help others if your family has no needs at all."]```

### qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_2
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Final options:
  - A. Words are eggs; when they drop on the floor, they shatter into pieces. (70 chars)
  - B. A farmer who finds a vessel without a neck must consult the village elders to learn how to tie it securely. (107 chars)
  - C. A white buttock is not a natural condition; for a farmer it happens when he rubs his buttocks in the dirt. (106 chars)
  - D. A vessel lacking a standard neck will eventually teach the farmer the unique method required to tie it securely. (112 chars)
- Raw model output:
  ```["A vessel lacking a standard neck will eventually teach the farmer the unique method required to tie it securely.", "A resourceful farmer will naturally invent a clever method to tie down a vessel that lacks a standard neck.", "A farmer who finds a vessel without a neck must consult the village elders to learn how to tie it securely.", "A vessel lacking a standard neck will be abandoned by a farmer who refuses to alter his traditional tying method."]```

## 6. Generator churn detail

- Active after preflight: qwen/qwen3.7-max, google/gemini-2.5-flash, google/gemma-4-31b-it
- Mid-run substitution: google/gemma-4-31b-it -> anthropic/claude-sonnet-4 (hard_fallback fail_count=2)
- Items contributed by Claude: 2 overgenerate-select items (1 partial, 1 hard_fallback in log)

## 7. Root-cause summary

1. **English too easy:** Prompt constraints successfully prevent paraphrase leakage, but they also push models toward obviously-wrong generic reversals. The hard-negative prompt is not producing subtle near-paraphrases.
2. **Yoruba abstract analogies:** Hard-negative and taxonomy prompts reward structurally parallel analogies ("A X shows the Y how to Z"). Auditors pick the more familiar abstract frame over the specific gourd/farmer image.
3. **Arabic generic idioms:** The expanded blocklist still misses some generic proverbs ("living dog/dead lion", "honey/stings"). More importantly, plausible community-oriented distractors still attract consensus.
4. **Length fallback persists:** The correct option is often longer than the distractors; even though v65 no longer counts it, distractor length outliers and duplicate-repair fallout still push items over the fallback threshold.
5. **Generator churn:** Gemma-4 is unstable and Claude-sonnet-4 is a poor substitute, making runs noisy.

## 8. Candidate v66 interventions (ranked by expected impact)

| Rank | Intervention | Why | Risk |
|---|---|---|---|
| 1 | Improve fallback distractor quality | Corpus fallbacks are the single biggest source of bad partial/HCW items. A lightweight LLM or template-based distractor generator would produce length-matched, semantically close wrong options. | Adds cost/complexity. |
| 2 | Harden English prompt | Explicitly forbid generic reversals and require distractors to be plausible alternative interpretations of the proverb. | May raise HCW if near-paraphrases survive. |
| 3 | Relax length threshold | Move to ±45% strict / ±55% relaxed to reduce length_fallback. | Could reintroduce length as a surface cue. |
| 4 | Stabilise generator roster | Remove claude-sonnet-4 from substitutes; use gemini-2.5-pro or gpt-4.1-mini. | May still face gemma-4 instability. |
| 5 | Make Yoruba meaning more distinctive | Add explicit causal/scoping language: "the unusual shape of the gourd itself tells the farmer how to tie it, without needing external advice." | Changes the gold standard. |
