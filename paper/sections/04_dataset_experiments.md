#### 4. Dataset and Experimental Setup

### 4.1 Languages and Corpora

| Language | Source | Size | Sampled | QA Coverage |
|----------|--------|------|---------|-------------|
| English | Compiled websites (scraped) | 2,278 proverbs | 60 (5 Ã— 12) | Not documented |
| Arabic | Academic dataset (source unknown) | 913 proverbs | 60 (5 Ã— 12) | Full |
| Yoruba | Owomoyela (2005) | 3,974 proverbs | 60 (5 Ã— 12) | 96.5% missing QA_Flag |

**Data provenance:** See `DATA_PROVENANCE_TEMPLATE.md`. Yoruba data is derived from a copyrighted book; the public release excludes raw Yoruba proverbs. Arabic source dataset is unidentified. English scraping sources are undocumented. These are limitations addressed in Section 10.

### 4.2 Gold-Meaning Curation

All three languages use LLM-curated gold meanings (`openai/gpt-4.1-nano`). Yoruba curation preserves gourd/farmer/bind imagery; Arabic curation preserves specific moral/social situations; English curation uses the original meaning if well-formed.

### 4.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Consensus accuracy | Fraction where plurality vote matches correct label | â€” |
| Perfect consensus | Fraction where all 4 auditors agree | < 30% |
| High-consensus-wrong (HCW) | Consensus fraction â‰¥ 0.75 and consensus â‰  correct | < 10% |
| Partial + fallback | Fraction with status `partial` or `length_fallback` | < 15% |
| Hard fallback (length parity) | Fraction with status `length_fallback` | < 5% |
| Duplicate options | Fraction with exact duplicate option pairs | 0% |
| Correct-key balance | Fraction per position A/B/C/D | ~25% each |

### 4.4 Committee Composition

| Model | Family | Role | Accuracy vs Gold |
|-------|--------|------|------------------|
| `meta-llama/llama-3.3-70b-instruct` | Meta | Auditor | 53.3% |
| `mistralai/mistral-small-3.2-24b-instruct` | Mistral | Auditor | 56.7% |
| `google/gemma-3-27b-it` | Google | Auditor | 45.6% |
| `deepseek/deepseek-v3.2` | DeepSeek | Auditor | 56.1% |

Pairwise Cohen's Îº: 0.485â€“0.555 (moderate agreement).

### 4.5 Statistical Methods

- Bootstrap 95% CIs: 10,000 resamples per metric.
- McNemar's test: paired variant comparisons on same 15 proverbs.
- Wilcoxon signed-rank: paired generator comparisons.
- Holm-Bonferroni correction: for 6 variant pairs + 3 generator pairs.

### 4.6 LLM-Proxy Inter-Annotator Agreement

Seven closed LLMs annotated a 60-item subset (20 per language). Fleiss Îº = 0.4845 (moderate agreement). Mean pairwise Cohen Îº = 0.4846. Per-model gold accuracy: 58.3â€“78.3%. This is treated as a standalone contribution, not a substitute for human validation.

---


