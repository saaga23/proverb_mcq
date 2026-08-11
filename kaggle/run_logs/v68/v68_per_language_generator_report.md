# v68 Per-language and per-generator/variant analysis

## Per-language metrics

**English** (n=60): consensus accuracy 65.0% (39/60), perfect 45.0%, HCW 33.3%
  key balance: A=15, B=15, C=15, D=15
  status: generated=48, partial=8, length_fallback=4
  mean fallback_count=0.43, nli=0.15, leak=0.15, length=0.07

**Arabic** (n=60): consensus accuracy 53.3% (32/60), perfect 50.0%, HCW 46.7%
  key balance: A=15, B=15, C=15, D=15
  status: generated=25, partial=21, length_fallback=14
  mean fallback_count=1.52, nli=0.62, leak=0.43, length=0.25

**Yoruba** (n=60): consensus accuracy 51.7% (31/60), perfect 30.0%, HCW 48.3%
  key balance: A=15, B=15, C=15, D=15
  status: generated=28, partial=21, length_fallback=11
  mean fallback_count=1.03, nli=0.32, leak=0.47, length=0.13

## Per-generator metrics

**google/gemini-2.5-flash** (n=60): accuracy 53.3%, perfect 41.7%, HCW 46.7%, generated=30/60
**google/gemma-4-31b-it** (n=60): accuracy 65.0%, perfect 46.7%, HCW 35.0%, generated=40/60
**qwen/qwen3.7-max** (n=60): accuracy 51.7%, perfect 36.7%, HCW 46.7%, generated=31/60

## Per-variant metrics

**adversarial-hard-negative** (n=45): accuracy 60.0%, perfect 31.1%, HCW 40.0%, generated=12/45
**adversarial-length-locked** (n=45): accuracy 55.6%, perfect 53.3%, HCW 44.4%, generated=27/45
**overgenerate-select** (n=45): accuracy 53.3%, perfect 35.6%, HCW 46.7%, generated=32/45
**taxonomy-guided** (n=45): accuracy 57.8%, perfect 46.7%, HCW 40.0%, generated=30/45

## Auditor behavior

**meta-llama_llama-3.3-70b-instruct** (n=180): missing 0/180 (0.0%), accuracy 56.7%
**mistralai_mistral-small-3.2-24b-instruct** (n=180): missing 0/180 (0.0%), accuracy 56.7%
**google_gemma-3-27b-it** (n=180): missing 0/180 (0.0%), accuracy 56.7%
**deepseek_deepseek-v3.2** (n=180): missing 0/180 (0.0%), accuracy 56.7%

## Overall cost and pool state
Estimated cost: $0.8539 / $5.0
Active generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash']
Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']

## Generator × status cross-tab

generation_status        generated  length_fallback  partial
generator_model                                             
google/gemini-2.5-flash         30                5       25
google/gemma-4-31b-it           40                6       14
qwen/qwen3.7-max                31               18       11

## Variant × status cross-tab

generation_status          generated  length_fallback  partial
variant                                                       
adversarial-hard-negative         12               19       14
adversarial-length-locked         27                9        9
overgenerate-select               32                1       12
taxonomy-guided                   30                0       15

## Language × status cross-tab

generation_status  generated  length_fallback  partial
language                                              
Arabic                    25               14       21
English                   48                4        8
Yoruba                    28               11       21

## Example HCW items

- google_gemini-2.5-flash_adversarial-length-locked_Arabic_1 (Arabic, google/gemini-2.5-flash, adversarial-length-locked, status=partial, consensus_frac=1.0, consensus_correct=0)
  correct meaning: Love is blind.
  A: Love can transform even the most humble offerings into something precious and valuable.
  B: Deep affection often blinds individuals to the imperfections of those they cherish.
  C: True devotion means accepting a partner's flaws without any desire for change.
  D: The believer is not bitten from the same hole twice

- qwen_qwen3.7-max_adversarial-length-locked_Arabic_2 (Arabic, qwen/qwen3.7-max, adversarial-length-locked, status=length_fallback, consensus_frac=0.75, consensus_correct=0)
  correct meaning: Charity begins at home.
  A: The stupid might want to help you, but they just ended up hurting you.
  B: Let them drink and forget their poverty and remember their misery no more.
  C: Individuals must prioritize supporting their immediate relatives before donating resources to the broader community.
  D: But remember that good intentions pave many roads. Not all of them lead to hell.

- google_gemma-4-31b-it_adversarial-length-locked_Arabic_3 (Arabic, google/gemma-4-31b-it, adversarial-length-locked, status=length_fallback, consensus_frac=1.0, consensus_correct=0)
  correct meaning: A bird in the hand is worth two in the bush.
  A: There is an excess of familiarity at the root of all hostilities.
  B: Better is a dinner of herbs where love is, than a stalled ox and hatred therewith.
  C: It is better to keep a small certainty than to risk it for a larger possibility.
  D: All is not gold that glitters All. 
Fine feathers do not make fine birds

- google_gemini-2.5-flash_adversarial-length-locked_Arabic_3 (Arabic, google/gemini-2.5-flash, adversarial-length-locked, status=partial, consensus_frac=1.0, consensus_correct=0)
  correct meaning: A bird in the hand is worth two in the bush.
  A: A small gain now is always preferable to the possibility of a larger future reward.
  B: One should always prioritize immediate gratification over long-term planning and investment.
  C: Time is like a sword; if you don't cut it, it will cut you
  D: It is better to hold onto what you have than to pursue something greater that is uncertain.

- qwen_qwen3.7-max_adversarial-length-locked_Arabic_4 (Arabic, qwen/qwen3.7-max, adversarial-length-locked, status=length_fallback, consensus_frac=1.0, consensus_correct=0)
  correct meaning: A bad workman always blames his tools.
  A: She blames her relatives for her own lack of good judgment.
  B: The end result of a good deed is a slap with the palms
  C: A bad workman always blames his tools.
  D: It's easier to give advice than to take it.
