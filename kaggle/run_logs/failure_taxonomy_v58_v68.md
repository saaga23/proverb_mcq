# ProverbGap Pilot 1 TEST — Failure Taxonomy & Intervention History (v58–v68)

**Scope:** OpenRouter distractor-generation notebook `abrahamsunday123/mcq-pass-shortcut`, versions 58–68.  
**Dates:** 2026-06-20 to 2026-06-22.  
**Source documents:** `AGENTS.md`, `memory.md`, `kaggle_run_logs/quality_analysis_report.md`, `kaggle_run_logs/v*/v*_detailed_analysis_report.md`.

---

## 1. Run-by-run summary table

| Version | Date | N / proverbs | Cost (USD) | Perfect consensus | HCW | Partial + fallback | English % | Arabic % | Yoruba % | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| v58 | 2026-06-20 | 1 / 3 | $0.2237 | 48.9% | 22.2% | 28.9% | 86.7% | 53.3% | 40.0% | 2 duplicate options; hard fallback 24.4% |
| v59 | 2026-06-20 | 1 / 3 | $0.1864 | 37.8% | 28.9% | 42.2% | 80.0% | 46.7% | 26.7% | Starters benched; EOL auditor removed |
| v60 | 2026-06-20 | 1 / 3 | $0.2288 | 44.4% | 28.9% | 48.9% | 80.0% | 40.0% | 26.7% | Leak sanitizer converted to per-distractor replacement; soft-fail threshold raised |
| v61 | 2026-06-20 | 1 / 3 | $0.1864 | 47.2% | 25.0% | 47.2% | 91.7% | 58.3% | 33.3% | Length ±20% → ±30%; `adversarial-contrastive` retired |
| v63 (v62 code) | 2026-06-21 | 1 / 3 | $0.1909 | 52.8% | 33.3% | 36.1% | 100.0% | 41.7% | 25.0% | Length ±30% → ±35% + relaxed all-within; per-language leak thresholds; Yoruba gold curation; offensive fallback guard |
| v64 | 2026-06-21 | 1 / 3 | $0.1703 | 47.2% | 19.4% | 41.7% | 91.7% | 58.3% | 50.0% | Gold curation extended to all languages; expanded idiom blocklist; per-language NLI embedding guard |
| v65 | 2026-06-21 | 1 / 3 | $0.1879 | 41.7% | **11.1%** | 36.1% | 100.0% | 50.0% | 41.7% | Option-level blocklist; correct-option length outlier excluded from fallback count; English NLI guard raised to 0.58 |
| v66 | 2026-06-21 | 1 / 3 | $0.1754 | 55.6% | 22.2% | 50.0% | 100.0% | 58.3% | 50.0% | Prompt hardening + length relaxation backfired; NLI replacements doubled (8 → 16) |
| v67 | 2026-06-21 | 1 / 3 | $0.1718 | — | — | — | — | — | — | Pushed but ran stale N=1 output; no reliable metrics |
| **v68** | **2026-06-22** | **5 / 15** | **$0.8539** | **41.7%** | **27.8%** | **43.9%** | **65.0%** | **53.3%** | **51.7%** | **Frozen v67 config; first scaled N=5 test; all shortcut-resistance gates failed except duplicates/key balance** |

*Targets: perfect consensus <30%, HCW <10% (step <15%), partial+fallback <15%, per-language consensus correctness ≥50%, 0 duplicates, balanced A–D keys, cost <$5.00.*

---

## 2. Failure taxonomy

### 2.1 Generic shortcut

**What it looks like:** Distractors are obvious reversals, generic life advice, or well-known English idioms/proverbs that auditors can dismiss without engaging the source proverb. English consensus correctness stayed at 91.7–100% through v61–v66; v68 English still 65.0% accuracy / 45.0% perfect consensus.

**Runs observed:** v58–v68 consistently. Examples:
- v58 English: *“Comfort builds resilience”*, *“Stay positive in adversity”*.
- v61 English: 91.7% consensus correct, mean consensus fraction 0.90.
- v63/v64: English 91.7–100% consensus correct.
- v68: English 65.0% accuracy, still the easiest language; `overgenerate-select` HCW 46.7%.

**Fixes tried:**
- v59: expanded `_GENERIC_ENGLISH_IDIOM_BLOCKLIST` with v58 leakages (*east or west home is best*, *go big or go home*, *make a rod for one's own back*).
- v61: removed `adversarial-contrastive` variant for producing near-paraphrases.
- v64: expanded blocklist with *People in glass houses…*, *The proof is in the pudding*, *Speech is silver…*, *Mind your own business*, etc.
- v65: made blocklist option-level (`skip_correct_option=True`) so the correct option is not rejected.
- v66: added explicit prompt constraints banning generic reversals and unrelated English idioms.

**Effect:** Blocklist reduced duplicates and parse-fallbacks, but English distractors remained too obviously wrong; v66 prompt hardening did not lower English consensus correctness.

---

### 2.2 Near-paraphrase trap

**What it looks like:** Models generate tempting, proverb-specific distractors that are semantically close to the correct meaning; NLI/correct-meaning-leak filters flag them and replace them with corpus fallbacks. This raises partial+fallback and, when the fallback is itself plausible, HCW.

**Runs observed:** v59 (9 NLI replacements), v60 (9), v61 (10), v63 (5, suppressed guard), v64 (10), v65 (8), v66 (16), v68 (mean 0.36 NLI replacements/MCQ, 0.35 leak replacements/MCQ).

**Fixes tried:**
- v59: added NLI paraphrase filter with embedding guard 0.55 to suppress false positives.
- v60: converted `has_correct_meaning_leak()` from whole-item rejection to per-distractor sanitizer.
- v61: widened semantic-distance band (default 0.82 → 0.85, Yoruba 0.85 → 0.88).
- v62/v63: per-language leak thresholds (English 0.90, Arabic/Yoruba 0.80); per-language semantic band (English 0.88, default 0.86, Yoruba 0.90).
- v64: lowered Arabic/Yoruba NLI embedding guard to 0.45; raised English to 0.58 in v65.
- v66: further length relaxation (±45%/±55%) and prompt hardening.

**Effect:** Tuning the guard was a seesaw. Lowering the guard in v64 cut HCW from 33.3% (v63) to 19.4%; raising English guard in v65 helped keep English HCW low. In v66, prompt hardening caused NLI replacements to double (8 → 16) and partial+fallback to rise to 50.0%. At N=5 (v68), NLI and leak filters became the dominant rewriters, driving 43.9% partial+fallback.

---

### 2.3 Confident-wrong fallback

**What it looks like:** After a model-generated distractor is rejected, the corpus fallback sampler draws a meaning from another proverb. That fallback is often plausible enough for 3/4 auditors to agree on it, but it is wrong.

**Runs observed:** v58 (22.2%), v59 (28.9%), v60 (28.9%), v61 (25.0%), v63 (33.3%), v64 (19.4%), v65 (11.1%), v66 (22.2%), v68 (27.8%).

**Fixes tried:**
- v59: hardened fallback sampler with length-ratio filtering, exclude sets, weighted-random selection.
- v60–v65: iterated leak/NLI/length thresholds to reduce rejections and therefore fallback use.
- v62: added offensive/inappropriate fallback blocklist.
- v65: stopped counting `dup_replaced` and correct-option length outliers as fallback, improving status labels.

**Effect:** Sampler tweaks reduced collisions and offensive outputs but did not fix the core problem: random corpus meanings are not proverb-specific hard negatives. v68 confirmed this at scale — mean 0.99 corpus replacements/MCQ, and HCW jumped from 11.1% (v65 N=1) to 27.8% (v68 N=5). The `adversarial-hard-negative` variant was most damaged: only 26.7% fully generated, 42.2% length_fallback, 40.0% HCW.

---

### 2.4 Cultural mismatch

**What it looks like:** For Arabic and Yoruba, distractors or corpus fallbacks contain generic English idioms, vulgar text, or culturally mismatched proverbs that do not belong in a low-resource-language item.

**Runs observed:** v58–v68, especially Yoruba. Examples:
- v61 Yoruba: fallback distractor *“One should not attempt to scare an old [woman] with a huge penis.”*
- v63 Arabic: *People in glass houses…*, *The smarter you are…*, *Speech is silver…* leaked into distractors.
- v64: Arabic gold meaning *“Charity begins at home”* caused correct option to be blocklisted.
- v65/v66: Yoruba hard-negative distractors were structurally parallel analogies (*A cracked clay pot shows the potter…*) that auditors preferred over the gourd/farmer key.

**Fixes tried:**
- v2.2/v59: added ~120-entry Yoruba English-idiom blocklist with fuzzy matching.
- v62: added Yoruba gold-meaning curation (`curate_yoruba_meaning`) using `gpt-4.1-nano`.
- v64: extended curation to all languages; improved Yoruba prompt to preserve gourd/farmer/bind imagery.
- v65: option-level blocklist fix prevented the Arabic *“Charity begins at home”* correct option from being rejected.

**Effect:** Yoruba correctness improved from 25–33% in v61–v63 to 50% in v64/v66, but remained fragile (41.7% in v65, 51.7% in v68). Cultural mismatch shifted from obvious English idioms to plausible but culturally generic analogies.

---

### 2.5 Length / register imbalance

**What it looks like:** One option is much longer/shorter than the others, creating a surface cue; or the correct meaning is an outlier and the item is misclassified as fallback.

**Runs observed:**
- v58: 7 length_fallback / 45 (15.6%).
- v60: 13 length_fallback / 45 (31.1%) — worst length fallout.
- v61: 6 length_fallback / 36 (16.7%).
- v63: 3 length_fallback / 36 (8.3%).
- v65: 4 length_fallback / 36 (11.1%).
- v66: 2 length_fallback / 36 (5.6%) but 16 partial (NLI-driven).
- v68: 29 length_fallback / 180 (16.1%), but length replacements were only mean 0.15/MCQ; NLI/leak dominated.

**Fixes tried:**
- v59/v60: length check reference changed from correct-meaning-only to median of all four options.
- v61: `LENGTH_CHECK_THRESHOLD` 0.20 → 0.30.
- v62: 0.30 → 0.35 + `LENGTH_RELAXED_THRESHOLD = 0.45`; `length_fallback` status only when `length_replaced >= 2`.
- v66: 0.35 → 0.45 / 0.45 → 0.55.
- v67/v68: reverted to v65 thresholds (±35%/±45%).
- v65: correct-option length outliers recorded separately, not counted as fallback.

**Effect:** Length relaxation consistently reduced raw `length_fallback` counts, but the rejected distractors often became `partial` items via NLI/leak rewrites rather than truly accepted. v68 shows length is now a minor driver; the bottleneck is NLI/leak fallback quality, not length.

---

## 3. Repeated / ineffective interventions vs. new levers

### Repeated or ineffective

| Intervention | First seen | Repeated in | Outcome |
|---|---|---|---|
| Length-threshold relaxation | v61 (0.20→0.30) | v62 (0.30→0.35), v66 (0.35→0.45) | Temporarily lowers `length_fallback` but items convert to `partial` or HCW; net partial+fallback stays >36% |
| Semantic / NLI guard tuning | v59 | v61, v62, v64, v65, v66 | Seesaw: lower guard cuts HCW but raises partial; higher guard reduces rewrites but lets paraphrases through |
| Generic-English idiom blocklist | v59 | v64, v65 | Stopped obvious leaks but did not make distractors subtle |
| Prompt hardening against generic reversals | v66 | — | Backfired: NLI replacements doubled, partial+fallback rose to 50.0%, HCW 22.2% |
| Gold-meaning curation | v62 (Yoruba) | v64 (all languages) | Helped Yoruba reach 50% but did not fix confident-wrong fallback or English too-easy problem |

### New or structurally different interventions

| Intervention | Version | Why it is new |
|---|---|---|
| Option-level idiom blocklist | v65 | Replaces only the offending distractor instead of rejecting the whole MCQ |
| Exclude correct-option length outliers from fallback count | v65 | Separates classification artefact from real distractor quality |
| `dup_replaced` excluded from fallback/partial status | v66 | Better bookkeeping, not a quality fix, but changes status interpretation |
| Stable reordered generator roster | v66/v67 | No mid-run substitutions in v66/v68, reducing roster noise |
| LLM-based fallback distractor generator | v69 | First change to the **fallback mechanism itself**; replaces corpus sampling with `gpt-4.1-nano` proverb-specific hard negatives |

---

## 4. Is v69 (LLM fallback) a repetition or a new lever?

**It is a new lever.**

All prior interventions (v58–v68) operated on the same corpus-based fallback architecture: tune filters, tune thresholds, tune prompts, then sample a replacement from other proverbs’ meanings. v58–v66 iterated length, leak, NLI, blocklist, and curation within that architecture; v67/v68 froze the best of those settings and scaled N from 1 to 5. The v68 N=5 run confirmed that the architecture itself hits a ceiling: 43.9% partial+fallback and 27.8% HCW, with corpus fallbacks as the dominant driver.

v69 changes the replacement source. Instead of `semantically_distinct_negative_sample()` drawing from the corpus, it calls `openai/gpt-4.1-nano` to generate a single proverb-specific hard negative on demand, with the same NLI/leak/length/idiom/offensive filters applied. It also adds proverb/variant context, symmetric NLI, temperature=0.0, and explicit counters for LLM fallback use/rejection.

If v69 reduces HCW and partial+fallback, the credit belongs to the new fallback mechanism, not to more threshold tuning. If it fails, the project will treat v68/v69 as the production dataset and frame the corpus-fallback bottleneck as a reproducible failure-mode contribution.

---

*Report generated 2026-06-22.*
