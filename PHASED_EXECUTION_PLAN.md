# Phased Execution Plan: Fix 14 Critical Bugs + Paper Reframe

## Phase 1: Fix All 14 Critical Bugs (Parallel Agents)

### Agent 1: `proverbgap_kaggle_final.py` (Source of Truth)
**Bugs to fix:**
- **#1 Eval prompt leak:** Remove `proverb_en` from `build_eval_prompt()` (proverb_en now = correct_meaning)
- **#5 best_effort = fallback:** Change `return best_options, False, ...` → `return best_options, True, ...`
- **#7 Few-shot always 'A':** Rotate answer positions in few-shot examples
- **#9 hash() non-deterministic:** Replace `hash(model)` with `hashlib.md5(model.encode()).hexdigest()`
- **#11 bootstrap_ci global RNG:** Use `np.random.default_rng(seed)` 
- **#12/#15 S1 fallback identical options:** Use distinct placeholders instead of `[proverb_en]*4`
- **#22 eval_worker hash() twice:** Same fix as #9 for both model_seed and idx hash

### Agent 2: `pilot_v2.py`
**Bugs to fix:**
- **#2 Default data dir:** Change `original_data` → `actual_data` in all defaults
- **#3 No QA_Flag filtering:** Add `df = df[df['QA_Flag'] != 'DROP']` in `_load_and_prepare_data()`
- **#4 max_tok=5:** Change `max_tok=5` → `max_tok=128` in `audit_one_model()`
- **#6 First-match extraction:** Switch `_RE_ANSWER_LETTER.search()` → `findall()` + take last
- **#10/#34 Preflight stale cache:** Add `skip_cache=True` to preflight probes
- **#17 Sample with replacement:** Change `replace=(n_sample < 3)` → always `replace=False`, pad with placeholders
- **#18 English-only validator:** Document limitation or switch to multilingual model
- **#20 Dual-gate OR not AND:** Document intentionally OR, or switch to AND with relaxed thresholds

### Agent 3: `proverbgap_minimal_local.py`
**Bugs to fix:**
- **#1 Eval prompt leak:** Remove `proverb_en` from `build_eval_prompt()`
- **#12/#15 S1 fallback identical options:** Use distinct placeholders
- **#28 Evaluates only 6 MCQs:** Change `mcqs_s1[:3] + mcqs_s2[:3]` → evaluate ALL generated
- **#29 max_tok=10:** Change `max_tok=10` → `max_tok=128`

### Agent 4: `evaluation_pilot.py` + `test_pilot_v2.py`
**Bugs to fix in evaluation_pilot.py:**
- **#1 Eval prompt leak:** Remove `proverb_en` from eval prompt
- **#2/#13/#26 Hardcoded original_data:** Change to `actual_data/`
- **#6/#23 First-match extraction:** Switch to last match
- **#14/#27 max_tok=5:** Change to `max_tok=128`
- **#8 Plurality not majority:** Change `max(set, key=...)` → require `count > len(preds)/2`
- **#24 Fallback first-char:** Use `findall` + take last

**Bugs to fix in test_pilot_v2.py:**
- **#2/#37 Hardcoded original_data:** Change all `--data-dir original_data` → `actual_data`
- **#39 No prompt leak test:** Add test asserting `correct_meaning` not in eval prompt output
- **#40 No unclosed tag test:** Add test for `<think>reasoning` (no closing tag)
- **#41 No truncation test:** Add test with mock "The answer is B" response

### Agent 5: Paper Reframe
**Tasks:**
- Write new paper title + abstract to `docs/ProverbGap_Reframed_Title_Abstract.md`
- Update introduction framing to foreground methodology + negative results
- Update `EACL_STRATEGY_SYNTHESIS.md` with "locked" decisions

## Phase 2: Validation (After Agent Completion)
- Run `test_pilot_v2.py` — must pass all tests
- Run `proverbgap_minimal_local.py` N=5 — must complete cleanly
- Verify eval prompts do NOT contain `correct_meaning`

## Phase 3: Data Provenance Sprint (Next Phase)
- Arabic HF source identification
- English scraping protocol documentation  
- Yoruba copyright permission letter template

## Phase 4: Scale + Human Validation (Future)
- N=700 per language run
- Native speaker recruitment
- 3rd model integration

---

**Target: Complete Phase 1 in this session. Phase 2 validation in same session. Phases 3-4 in subsequent sessions.**
