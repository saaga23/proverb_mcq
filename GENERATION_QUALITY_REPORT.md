# MCQ Generation Quality Analysis
**Log:** `last_run/mcq-pass-shortcut.log` (24,393 lines)  
**Focus:** Strategy 2 generation quality only (Strategy 1 had 0% fallback across all languages)

---

## 1. [LENGTH VALIDATION FAILED] Messages

| Metric | Value |
|--------|-------|
| **Total occurrences** | **296** |
| Attempt 1 failures | 144 |
| Attempt 2 failures | 93 |
| Attempt 3 failures | 59 |

> **Note:** The log interleaves concurrent Task A and Task B generation threads, so individual `[LENGTH VALIDATION FAILED]` lines do not carry explicit language/task tags. Language attribution is inferred from the fallback events (see Section 2).

### Option Length Statistics (1,184 individual option measurements)

| Statistic | Value |
|-----------|-------|
| **Minimum** | **12** characters |
| **Maximum** | **202** characters |
| **Average** | **58.0** characters |

### Option Length Distribution

| Bucket | Count | % of Total |
|--------|-------|------------|
| ≤ 25 chars | 97 | 8.2% |
| 26–50 chars | 347 | 29.3% |
| 51–75 chars | 429 | 36.2% |
| 76–100 chars | 193 | 16.3% |
| 101–150 chars | 87 | 7.3% |
| > 150 chars | 31 | 2.6% |

**Key observation:** 97 options (8.2%) were extremely short (≤ 25 chars) and 31 options (2.6%) were extremely long (> 150 chars), suggesting the length validator is rejecting both overly terse and overly verbose distractors.

---

## 2. [ALL LENGTH VALIDATIONS FAILED] Fallback Messages

| Metric | Value |
|--------|-------|
| **Total fallback events** | **68** |
| **Unique samples affected** | **56** |
| **Samples failing in BOTH tasks** | **12** |

### Fallback Events by Language (from sample IDs)

| Language | Fallback Events | Unique Samples | % of Lang Pool (30) |
|----------|-----------------|----------------|---------------------|
| **English** (ENG*) | 24 | ~20 | ~40% |
| **Yoruba** (YOR*) | 25 | ~21 | ~42% |
| **Arabic** (MID*) | 19 | ~15 | ~32% |

### Fallback Events by Task (exact rates from summary lines)

| Task | Arabic | English | Yoruba | Overall |
|------|--------|---------|--------|---------|
| **B-Strategy2** | 30.0% (9/30) | 40.0% (12/30) | **43.3%** (13/30) | **37.8%** (34/90) |
| **A-Strategy2** | 33.3% (10/30) | 40.0% (12/30) | 40.0% (12/30) | **37.8%** (34/90) |

**Key pattern:** Yoruba shows the highest fallback rate in Task B (43.3%). English is consistently problematic across both tasks (40.0% each). Arabic has the lowest fallback rate in Task B but rises slightly in Task A.

---

## 3. Samples with Repeated Failures (Both Tasks)

The following **12 samples** failed length validation in **both Task A and Task B** and were forced to fallback in both runs:

| Sample ID | Language | Sample ID | Language |
|-----------|----------|-----------|----------|
| ENG0701 | English | MID0068 | Arabic |
| ENG0787 | English | MID0071 | Arabic |
| ENG1323 | English | YOR1521 | Yoruba |
| ENG1484 | English | YOR2476 | Yoruba |
| ENG1798 | English | YOR4105 | Yoruba |
| ENG1901 | English | | |
| ENG2076 | English | | |

**Anomaly:** 7 of the 12 repeated failures are English samples, suggesting certain English proverbs consistently produce distractors that violate length constraints regardless of task variant.

---

## 4. [API FAIL] Messages During Generation

| Metric | Value |
|--------|-------|
| **Exact `[API FAIL]` matches** | **0** |

No log lines contain the literal string `[API FAIL]`.

### HTTP Errors Observed During Strategy 2 Generation (lines 9874–10614)

Despite the absence of `[API FAIL]` tags, **233 HTTP errors** occurred during generation:

| Provider | Error Code | Count | Issue |
|----------|-----------|-------|-------|
| **groq** | 400 Bad Request | **184** | Most frequent; suggests malformed requests or context-length issues |
| **llm7** | 429 Too Many Requests | **39** | Rate limiting |
| **deepinfra** | 402 Payment Required | **10** | Billing/quota exhaustion |

**Impact:** These errors are interleaved with length-validation attempts but do **not** appear to prevent eventual fallback (the system continues retrying). No generation crashes or unrecoverable failures were logged.

---

## 5. Strategy 2 JSON Output Validity

| Metric | Value |
|--------|-------|
| JSON parse errors during generation | **0** |
| Malformed JSON warnings | **0** |

**Assessment:** Strategy 2 generation produced **consistently valid JSON outputs**. This is inferred because:
- The length-validation logic extracts `Option lengths: [a, b, c, d]` from parsed JSON on every attempt.
- No `json.decode`, `JSONDecodeError`, or `malformed` messages appear in the generation section.
- The fallback mechanism triggers only on *length* constraints, never on *parsing* constraints.

---

## 6. Patterns: Language & Task Failure Rates

### Clear Patterns
1. **Yoruba is most brittle in Task B** – 43.3% fallback (13/30), the highest of any language-task combination.
2. **English is consistently problematic** – exactly 40.0% in both tasks, and 7 of the 12 cross-task repeat failures are English.
3. **Arabic is relatively robust** – lowest fallback rate in Task B (30.0%) and only slightly higher in Task A (33.3%).
4. **No difference in overall fallback rate between tasks** – both Task A and Task B show 37.8% overall fallback.

### Length Distribution Patterns
- **Short-option bias:** 97 generated options were ≤ 25 characters, indicating the model frequently produces overly brief distractors.
- **Long-tail outliers:** 31 options exceeded 150 characters, with the absolute maximum reaching **202 characters**.
- The validator appears to enforce a middle-length window (roughly ~25–120 chars), with the bulk of attempts (65.5%) falling in the 26–75 char range.

---

## 7. Generation Anomalies & Weird Outputs

### Repeated Failures on Identical Samples
- **12 samples** failed in both Task A and Task B (listed in Section 3).
- This indicates the length-validation issue is **sample-dependent**, not random noise.

### Extreme Option Lengths
- **Shortest recorded option:** 12 characters
- **Longest recorded option:** 202 characters
- Example extreme: `[178, 146, 162, 157]` (Attempt 2, line 9891)
- Example minimal: `[12, ?, ?, ?]` (present in the dataset; exact line not isolated due to interleaving)

### API Provider Issues
- **groq** returned 184 `400 Bad Request` errors during generation. This is anomalously high and suggests either:
  - Context length exceeding groq's limits for certain samples
  - Malformed payloads being sent to groq
- **llm7** hit rate limits (39× `429`).
- **deepinfra** returned quota errors (10× `402`).

### No Raw Output Logging
- The log does **not** contain raw generated text/snippets, so direct inspection of semantic weirdness (repetition, gibberish, off-topic distractors) is **not possible** from this log alone.

---

## Summary Table

| Item | Count / Rate |
|------|--------------|
| Total log lines | 24,393 |
| Strategy 1 fallback rate | **0.0%** (all languages) |
| Strategy 2 length-validation failures | **296** |
| Strategy 2 fallback events | **68** (56 unique samples) |
| Samples failing in both A & B | **12** |
| Exact `[API FAIL]` messages | **0** |
| HTTP errors during gen | **233** (groq 400 ×184, llm7 429 ×39, deepinfra 402 ×10) |
| JSON parse failures | **0** |
| B-Strategy2 overall fallback | **37.8%** |
| A-Strategy2 overall fallback | **37.8%** |
| Worst language-task combo | **Yoruba / Task B = 43.3%** |
