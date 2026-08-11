# v68 vs v69 Comparison Report (TEMPLATE)

v69 data not yet available. This is the v68-only baseline to be compared against v69.

## v68 aggregate metrics (corpus-fallback baseline)

|                            |          0 |
|:---------------------------|-----------:|
| n_mcqs                     | 180        |
| cost_usd                   |   0.853899 |
| perfect_consensus_rate     |   0.416667 |
| hcw_rate                   |   0.277778 |
| partial_plus_fallback_rate |   0.438889 |
| hard_fallback_rate         |   0.161111 |
| consensus_accuracy         |   0.566667 |
| mean_fallback_count        |   0.994444 |
| mean_length_replaced       |   0.15     |
| mean_leak_replaced         |   0.35     |
| mean_nli_replaced          |   0.361111 |
| duplicate_options_count    |   0        |

## v68 per-language metrics

| language   |   n |   consensus_accuracy |   accuracy_ci_low |   accuracy_ci_high |   perfect_consensus_rate |   hcw_rate |   partial_plus_fallback_rate |   hard_fallback_rate |   mean_fallback_count |   mean_nli_replaced |   mean_leak_replaced |   mean_length_replaced |
|:-----------|----:|---------------------:|------------------:|-------------------:|-------------------------:|-----------:|-----------------------------:|---------------------:|----------------------:|--------------------:|---------------------:|-----------------------:|
| Arabic     |  60 |             0.533333 |          0.408932 |           0.653723 |                     0.5  |   0.316667 |                     0.583333 |            0.233333  |              1.51667  |            0.616667 |             0.433333 |              0.25      |
| English    |  60 |             0.65     |          0.523624 |           0.758324 |                     0.45 |   0.183333 |                     0.2      |            0.0666667 |              0.433333 |            0.15     |             0.15     |              0.0666667 |
| Yoruba     |  60 |             0.516667 |          0.393076 |           0.638252 |                     0.3  |   0.333333 |                     0.533333 |            0.183333  |              1.03333  |            0.316667 |             0.466667 |              0.133333  |

Run `python compare_v68_v69.py` again after the v69 Kaggle output is copied to:
`C:\Users\USER\Downloads\THe proverbeval container\MCQ\kaggle_run_logs\v69\openrouter_pilot1_test_output`