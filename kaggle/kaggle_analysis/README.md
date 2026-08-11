<!-- ⚠️ DEPRECATED — 2026-06-19. This file describes the old Groq-based N=50 Kaggle analysis workflow. The active pilots are OpenRouter Pilot 1 TEST (distractor generation) and Pilot 2 v3 (S1/S2 evaluator). See ../AGENTS.md and preflight_audit_test_nano_opus.md for current instructions. -->

# Kaggle Run Analysis — ProverbGap N=50

## What to put here

### 1. Download from Kaggle Output
After your notebook run completes on Kaggle:

1. Go to Kaggle notebook → **Output** tab
2. Download these files:
   - `evaluation_results.csv`
   - `encoder_results.csv`
   - `mcqs_strategy1.csv`
   - `mcqs_strategy2.csv`
   - `.api_cache.sqlite` (optional, for cache analysis)
3. Place them in `kaggle_analysis/input/`

### 2. Download Kaggle Logs
From Kaggle notebook → **Logs** tab:
- Download the full log file
- Place it in `kaggle_analysis/input/kaggle_log.txt`

### 3. Run Analysis
```bash
cd kaggle_analysis
python analyze_kaggle_run.py
```

This generates:
- `analysis_output/main_results_table.csv`
- `analysis_output/per_model_breakdown.csv`
- `analysis_output/per_language_breakdown.csv`
- `analysis_output/position_bias_report.csv`
- `analysis_output/statistical_tests.csv`
- `analysis_output/error_analysis.csv`
- `reports/scale_readiness_report.md`

## Scale Readiness Check
Before scaling from N=50 → N=700, we verify:
- [ ] Fallback rate < 20% (S2 generation quality)
- [ ] API failure rate < 5% (key/provider health)
- [ ] Position bias is mitigated (chi² p > 0.05)
- [ ] Encoder baselines load successfully
- [ ] No model-specific systematic errors
- [ ] Contamination filter working
- [ ] Cache hit rate reasonable (for re-runs)
