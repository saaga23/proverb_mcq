<!-- ⚠️ DEPRECATED — 2026-06-19. This is the old v4.1 N=50 scale-readiness report from the Groq-based pipeline. The active roadmap is now OpenRouter Pilot 1 TEST → Pilot 2 v3 → human validation. Retained for historical context only. -->

# Scale Readiness Report — ProverbGap N=50 → N=700

## Executive Summary

**Overall: BLOCKERS FOUND**

## Individual Checks

| Check | Status | Value | Threshold |
|-------|--------|-------|-----------|
| S2 Fallback Rate | FAIL | 37.3% | < 20% |
| API Failure Rate | FAIL | 90.4% | < 5% |
| Encoder Baselines | PASS | 1200 rows | > 0 |
| Data Loaded | PASS | 2700 rows | > 0 |
| MCQs Generated | PASS | S1:150, S2:150 | > 0 |

## Key Metrics

- **S1 Overall Accuracy**: 14.7%
- **S2 Pipeline Accuracy**: 0.0%
- **S2 Strict Accuracy**: 0.0%
- **Total API Evaluations**: 2700
- **Total Encoder Evaluations**: 1200

## Per-Model API Performance

- **allam-2-7b**: S1=12.4%, S2=0.0%, Failures=843
- **llama-3.3-70b-versatile**: S1=15.1%, S2=0.0%, Failures=804
- **meta/llama-4-maverick-17b-128e-instruct**: S1=16.4%, S2=0.0%, Failures=793

## Recommendations for N=700 Scale

- **CRITICAL**: S2 fallback rate is too high. Improve generation prompt or increase MAX_RETRIES before scaling.
- **CRITICAL**: API failure rate is too high. Verify all keys are active and providers are healthy.