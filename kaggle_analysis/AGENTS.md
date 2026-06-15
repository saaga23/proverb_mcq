# Multi-Agent Analysis Framework

After you place your Kaggle output in `input/`, run these agents for comprehensive analysis.

## Agent 1: Data Quality Auditor
`python agents/agent_data_quality.py`
- Checks CSV integrity, missing values, duplicates
- Validates MCQ structure (4 options, correct answer present)
- Flags corrupted or incomplete rows

## Agent 2: API Health Monitor
`python agents/agent_api_health.py`
- Analyzes error patterns per provider/model
- Computes failure rates, latency distributions
- Identifies rate-limiting events
- Recommends key rotation adjustments

## Agent 3: Position Bias Detector
`python agents/agent_position_bias.py`
- Chi-square test per strategy
- Per-model position preference analysis
- Visual position bias heatmap

## Agent 4: Statistical Significance Tester
`python agents/agent_statistics.py`
- McNemar's test (S1 vs S2)
- Bootstrap confidence intervals
- Per-language significance testing
- Effect size computation

## Agent 5: Encoder Baseline Analyst
`python agents/agent_encoder_analysis.py`
- Per-encoder accuracy breakdown
- Language-specific encoder performance
- Similarity score distributions
- Comparison with API model performance

## Agent 6: Scale Readiness Assessor
`python agents/agent_scale_readiness.py`
- Computes all P0 readiness metrics
- Estimates runtime for N=700
- Identifies bottlenecks
- Produces go/no-go recommendation

## Run All Agents
```bash
python run_all_agents.py
```

This generates a unified report in `reports/unified_analysis_report.md`.
