#### 5. Main Results

### 5.1 Aggregate Metrics

| Metric | v68 N=5 | 95% Bootstrap CI | Target | Pass? |
|--------|---------|------------------|--------|-------|
| Consensus accuracy | 56.7% | [49.4%, 63.9%] | â€” | â€” |
| Perfect consensus | 41.7% | [34.4%, 48.9%] | < 30% | âŒ |
| HCW | 27.8% | [21.1%, 34.4%] | < 10% | âŒ |
| Partial + fallback | 43.9% | [36.7%, 51.1%] | < 15% | âŒ |
| Hard fallback (length parity) | 16.1% | [11.1%, 21.7%] | < 5% | âœ… |
| Duplicate options | 0.0% | [0.0%, 0.0%] | 0% | âœ… |
| Correct-key balance | 45/45/45/45 | â€” | ~25% | âœ… |

**Key finding:** The pipeline achieves zero infrastructure failures (API/parse fallback, benched generators, missing votes) but fails all shortcut-resistance gates except duplicates and key balance. The failure modes are systematic, not stochastic. Consensus is incorrect on 43.3% of items (100% − 56.7% accuracy); of these, 27.8% reach high-consensus-wrong (≥0.75 auditor agreement on the wrong option), and 16.1% carry the length-fallback status.

### 5.2 Per-Language Results

| Language | MCQs | Consensus Accuracy | 95% CI | Perfect Consensus | HCW |
|----------|------|-------------------|--------|-------------------|-----|
| English | 60 | 65.0% | [53.3%, 76.7%] | 45.0% | 18.3% |
| Arabic | 60 | 53.3% | [40.0%, 65.0%] | 50.0% | 31.7% |
| Yoruba | 60 | 51.7% | [38.3%, 65.0%] | 30.0% | 33.3% |

English is numerically easier than Arabic and Yoruba, but the 95% CIs overlap (English [53.3%, 76.7%], Arabic [40.0%, 65.0%], Yoruba [38.3%, 65.0%]), so the gap is not statistically distinguishable at N = 60 per language. Arabic and Yoruba have overlapping CIs, indicating similar difficulty levels.

### 5.3 Per-Generator Results

| Generator | MCQs | Consensus Accuracy | HCW | Partial+Fallback |
|-----------|------|-------------------|-----|------------------|
| `google/gemma-4-31b-it` | 60 | 65.0% | 21.7% | 33.3% |
| `google/gemini-2.5-flash` | 60 | 53.3% | 31.7% | 50.0% |
| `qwen/qwen3.7-max` | 60 | 51.7% | 30.0% | 48.3% |
| **Pooled** | **180** | **56.7%** | **27.8%** | **43.9%** |

Gemma-4-31b-it is the strongest generator (65.0% accuracy, 21.7% HCW). The pooled result (56.7%) is worse than gemma-only, suggesting that weaker generators introduce more HCW items than the pool diversity helps.

### 5.4 Position Bias

Correct-key distribution is perfectly balanced: 45/45/45/45 across all 180 MCQs. Committee accuracy by position:

| Position | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| A | 33 | 45 | 73.3% |
| B | 26 | 45 | 57.8% |
| C | 22 | 45 | 48.9% |
| D | 21 | 45 | 46.7% |

Chi-square goodness-of-fit: Ï‡Â² = 3.49, df = 3, p = 0.322. **Not significant** at Î± = 0.05. The position-bias trend is present but does not reach significance at N = 180. Balanced key distribution means the raw consensus accuracy is unbiased, but variance by position suggests committee calibration issues.

### 5.5 Infrastructure Robustness

| Metric | v58â€“v63 legacy | v68 current |
|--------|---------------|-------------|
| Hard fallback rate (infrastructure/API) | 90%+ API failures | **0%** |
| Parse fallback rate | Provider cascades | **0%** |
| Benched generators | Model EOL crashes | **0%** |
| Missing audit votes | Missing votes | **0%** |
| Duplicate options | Not tracked | **0%** |

The hardened dynamic pool eliminates all infrastructure failures (API/parse fallback, benched generators, missing votes) observed in earlier runs. Separately, the length-parity fallback *status* affects 16.1% of MCQs (see §5.1), a distinct metric from infrastructure hard-fallback.

---


