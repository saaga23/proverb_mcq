# Audit Behavior Analysis Report
## Log: `last_run/mcq-pass-shortcut.log` (24,393 lines)

---

## 1. Committee Consensus SRS by Audit File & Language

| Audit File | Language | Consensus SRS | 95% CI |
|---|---|---|---|
| **a_strat1** | English | 20.0% | 5.7% – 34.3% |
| **a_strat1** | Yoruba | 10.0% | 0.0% – 20.7% |
| **a_strat1** | Arabic | 20.0% | 5.7% – 34.3% |
| **a_strat2** | English | 40.0% | 22.5% – 57.5% |
| **a_strat2** | Yoruba | 26.7% | 10.8% – 42.5% |
| **a_strat2** | Arabic | 26.7% | 10.8% – 42.5% |
| **b_strat1** | English | 16.7% | 3.3% – 30.0% |
| **b_strat1** | Yoruba | 10.0% | 0.0% – 20.7% |
| **b_strat1** | Arabic | 20.0% | 5.7% – 34.3% |
| **b_strat2** | English | 16.7% | 3.3% – 30.0% |
| **b_strat2** | Yoruba | 26.7% | 10.8% – 42.5% |
| **b_strat2** | Arabic | 20.0% | 5.7% – 34.3% |

> **Note:** Results are derived from the grid summary at the end of the log (line 24357) and cross-referenced with the per-audit consensus printouts.

---

## 2. Committee Response Shrinkage ("Only X/5 models responded")

### Overall (360 items across 4 audits)

| Models Responding | Count | % of Total |
|---|---|---|
| Only 2/5 | **276** | **76.7%** |
| Only 3/5 | **11** | **3.1%** |
| Only 4/5 | **73** | **20.3%** |
| 5/5 | 0 | 0.0% |
| 0/5 | 0 | 0.0% |

### Per Audit Breakdown

| Audit | 2/5 | 3/5 | 4/5 | Total |
|---|---|---|---|---|
| a_strat1 | 47 | 7 | 36 | 90 |
| a_strat2 | 90 | 0 | 0 | 90 |
| b_strat1 | 49 | 4 | 37 | 90 |
| b_strat2 | 90 | 0 | 0 | 90 |

---

## 3. Models Most Often Missing from Committee Responses

### Completely Non-Responsive (0 hits across all items in an audit)

| Model | a_strat1 | a_strat2 | b_strat1 | b_strat2 | **Total Missing** |
|---|---|---|---|---|---|
| `qwen3-32b` | 90/90 | 90/90 | 90/90 | 90/90 | **360/360 (100%)** |
| `llama-3.2-11b-vision-preview` | 79/90 | 90/90 | 80/90 | 90/90 | **339/360 (94%)** |
| `llama-3.2-3b-preview` | 81/90 | 90/90 | 80/90 | 90/90 | **341/360 (95%)** |

### Mostly Responsive

| Model | a_strat1 | a_strat2 | b_strat1 | b_strat2 |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | 64/90 zeros | 42/90 zeros | 71/90 zeros | 61/90 zeros |
| `llama-3.1-8b-instant` | 61/90 zeros | 54/90 zeros | 70/90 zeros | 61/90 zeros |

> **Interpretation:** `qwen3-32b` failed to respond in **every single audit item** (100% outage). The two smaller Llama models (`11b-vision` and `3b-preview`) were also catastrophic failures, missing on **94–95%** of all items. Only the two largest models (`70b-versatile` and `8b-instant`) maintained meaningful uptime.

### Root Cause from Log

- **15,131** HTTP 400 errors from `groq`
- **5,276** HTTP 429 errors from `llm7`
- **1,739** HTTP 402 errors from `deepinfra` (Payment Required)
- **1,176** total "All providers failed" events:
  - `llama-3.2-3b-preview`: 591 failures
  - `llama-3.2-11b-vision-preview`: 585 failures

The `qwen3-32b`, `llama-3.2-11b-vision-preview`, and `llama-3.2-3b-preview` models rely heavily on `groq`, `llm7`, and `deepinfra`. The widespread provider failures (especially groq 400s and llm7 429s) explain why these models were almost entirely absent from the committee.

---

## 4. Audit Items Where ALL 5 Models Failed to Respond

**Count: 0 items**

There were **no instances** of 0/5 model response across any of the 360 audited items. Even in the worst-case audits (a_strat2 and b_strat2), at least 2 models (`llama-3.3-70b-versatile` and `llama-3.1-8b-instant`) consistently responded.

---

## 5. Consensus Vote vs. Model Availability Correlation

| Audit | 2/5 Responded | 3/5 Responded | 4/5 Responded |
|---|---|---|---|
| **a_strat1** | 14.9% (47 items) | 0.0% (7 items) | 22.2% (36 items) |
| **b_strat1** | 18.4% (49 items) | 0.0% (4 items) | 13.5% (37 items) |
| **a_strat2** | 31.1% (90 items) | — | — |
| **b_strat2** | 21.1% (90 items) | — | — |

### Observations

- **No clear positive correlation** between more models responding and higher consensus accuracy.
- In `a_strat1`, 4/5 responded yielded the highest accuracy (22.2%), but 3/5 responded yielded **0.0%** — worse than 2/5 (14.9%). The 3/5 bucket has only 7 items, making it statistically noisy.
- In `b_strat1`, 2/5 responded (18.4%) actually outperformed 4/5 responded (13.5%).
- The low sample sizes for 3/5 and 4/5 buckets (4–37 items) make it difficult to draw a firm statistical conclusion, but the data does **not** support the hypothesis that "more available models → more accurate consensus."

---

## 6. Audit Accuracy: Strategy 1 vs Strategy 2

### Overall Consensus Accuracy

| Task | Strategy 1 | Strategy 2 | Δ (S2 − S1) |
|---|---|---|---|
| **Task A (Literal)** | 16.7% | 31.1% | **+14.4 pp** |
| **Task B (Cultural)** | 15.6% | 21.1% | **+5.6 pp** |

### Per-Language Breakdown

**Task A:**
- English: S1=20.0% → S2=40.0% (**+20.0 pp**)
- Yoruba: S1=10.0% → S2=26.7% (**+16.7 pp**)
- Arabic: S1=20.0% → S2=26.7% (**+6.7 pp**)

**Task B:**
- English: S1=16.7% → S2=16.7% (**0.0 pp**)
- Yoruba: S1=10.0% → S2=26.7% (**+16.7 pp**)
- Arabic: S1=20.0% → S2=20.0% (**0.0 pp**)

### Key Pattern

- **Strategy 2 is consistently more exploitable** (higher consensus accuracy) than Strategy 1 in 5 out of 6 task-language combinations.
- The effect is strongest in **Task A (+14.4 pp overall)** and in **English/Yoruba**.
- Strategy 2's LLM-paraphrased correct answers apparently introduce stylistic cues that the committee models can exploit, even though the generation was intended to neutralize such biases.

### Individual Model Performance (Strategy 1 vs Strategy 2)

| Model | Task A S1 | Task A S2 | Task B S1 | Task B S2 |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | 28.9% | 53.3% | 21.1% | 32.2% |
| `llama-3.1-8b-instant` | 32.2% | 40.0% | 22.2% | 32.2% |
| `llama-3.2-11b-vision-preview` | 12.2% | 0.0%* | 11.1% | 0.0%* |
| `llama-3.2-3b-preview` | 10.0% | 0.0%* | 11.1% | 0.0%* |
| `qwen3-32b` | 0.0%* | 0.0%* | 0.0%* | 0.0%* |

\* Model was completely non-responsive in this audit.

---

## 7. Audit Anomalies

### Invalid / Anomalous Model Responses

| Anomaly Type | Count | Evidence |
|---|---|---|
| Empty/whitespace API responses | **0** | No `[API Empty]` lines in log |
| `None` responses in audit context | **0** | No `None` mentions in audit-related log lines |
| Multi-letter answers (e.g., "AB", "BC") | **0** | No invalid multi-letter patterns found |
| Non-A-D answers | **0** | No non-A-D answer strings detected |

### Provider-Level Anomalies

| Provider | Error Type | Count |
|---|---|---|
| `groq` | HTTP 400 Bad Request | 15,131 |
| `llm7` | HTTP 429 Too Many Requests | 5,276 |
| `deepinfra` | HTTP 402 Payment Required | 1,739 |

- **No providers were permanently disabled** via the `[DISABLED]` cooldown mechanism (0 occurrences).
- **No providers entered the 120-second cooldown** (`[COOLDOWN]`: 0 occurrences).
- The overwhelming majority of failures are **groq 400 errors** (bad request), suggesting the model IDs sent to groq were rejected, possibly due to model deprecation or malformed routing.

### Summary

The audit was **not** marred by models returning syntactically invalid answers (None, empty strings, multi-letter responses). Instead, the dominant anomaly was **catastrophic model unavailability**: three of the five committee models (`qwen3-32b`, `llama-3.2-11b-vision-preview`, `llama-3.2-3b-preview`) were effectively absent from ~94–100% of audit items due to cascading provider API failures.

---

## Appendix: Methodology

- **Shrinkage-to-audit mapping:** Determined by identifying four consecutive blocks of 90 `[COMMITTEE SHRINKAGE]` lines each, then matching each block to the nearest subsequent consensus SRS printout. The mapping was validated against the final grid summary.
- **Missing-model inference:** Models with 0 hits in an entire audit (90/90 zeros) are classified as "completely missing." For Strategy 1 audits, the shrinkage counts (2/5, 3/5, 4/5) were cross-referenced with model hit rates to infer which specific models were absent.
- **Correlation analysis:** Consensus hit rates were computed per response-count bucket by aligning the 90 CSV rows per audit with the 90 shrinkage log lines in order.
