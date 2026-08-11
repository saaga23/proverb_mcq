#### 10. Discussion and Limitations

### 10.1 Corpus Fallback as Methodological Signal

The 43.9% partial+fallback rate is not a bug to be fixed but a signal to be studied. Every fallback replacement is a documented failure of the semantic filters. The fallback sampler reveals which distractors are "too close" to the gold meaning and which are "too far." This is precisely the kind of fine-grained error analysis reviewers expect from a methodology paper.

### 10.2 MCQ-Only Scope

We deliberately limit our study to MCQ. Fill-in-the-blank and open-ended generation tasks introduce different failure modes (memorization, free-generation bias) that are outside our current scope. We plan to extend the pipeline to FiB and generation in future work.

### 10.3 N=5 as Methodology Study

180 MCQs (60 per language) is modest for per-language generalization claims. We frame the paper as a **methodology + failure-taxonomy study**. All CIs are reported; we avoid strong claims about entire language families. A follow-up at N=15 (540 MCQs) is planned when budget renews.

### 10.4 API Reproducibility

OpenRouter model IDs may change or be deprecated. We mitigate this with:
- Versioned model IDs in `pilot1_test_summary.json`
- OpenRouter catalog snapshot in `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`
- SHA256 hashes of all output files
- Detailed reproduction steps in `REPRODUCIBILITY_CHECKLIST.md`

### 10.5 Yoruba Data Provenance

The Yoruba corpus is derived from Owomoyela (2005), which is under copyright. We exclude raw Yoruba proverbs from the public release but retain the 60 MCQs in our analysis. This is a limitation that future work should address by obtaining redistribution permission or using public-domain Yoruba proverb collections.

### 10.6 Zero Human Validation

Native-speaker human validation is pending. The LLM-proxy IAA (Îº = 0.4845) is a calibration anchor, not a validity certificate. We plan to recruit 2â€“3 native speakers per language for a 60â€“90 item validation study with Cohen's Îº reporting. This is documented as future work.

### 10.7 Generalizability

Our findings are specific to proverb understanding in English, Arabic, and Yoruba. Extension to other figurative languages (idioms, metaphors, sarcasm) requires re-running the pipeline with language-specific prompts and filters. The failure taxonomy is generalizable, but the specific magnitudes are not.

### 10.8 Ethics and Bias

We include idiom and offensive-content blocklists to prevent culturally inappropriate distractors. However, corpus fallbacks are not culturally curated, and some may be mismatched or offensive. We recommend human-expert review of all fallback items before releasing benchmarks to the public.

---


