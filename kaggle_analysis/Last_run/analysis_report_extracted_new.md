
## 1. Row counts and completeness
eval_results.csv: 900 rows x 11 cols
eval_results_progress.csv: 900 rows; identical to eval_results: False
Column null counts in eval_results:
|              |   null_count |
|:-------------|-------------:|
| sample_id    |            0 |
| language     |            0 |
| strategy     |            0 |
| model        |            0 |
| style        |            0 |
| predicted    |          135 |
| correct      |            0 |
| match        |          135 |
| raw_response |          135 |
| error        |          765 |
| failed       |            0 |
summary_stats.csv: 32 rows x 10 cols
Rows per strategy-language in summary_stats:
| strategy   | language   |   rows |
|:-----------|:-----------|-------:|
| S1         | ALL        |      4 |
| S1         | Arabic     |      4 |
| S1         | English    |      4 |
| S1         | Yoruba     |      4 |
| S2         | ALL        |      4 |
| S2         | Arabic     |      4 |
| S2         | English    |      4 |
| S2         | Yoruba     |      4 |
mcqs_s1.csv: 150; mcqs_s2.csv: 150; mcqs_all.csv: 300
Expected MCQs = 300; actual = 300; missing = 0

## 2. Failure rates
Overall failures: 135/900 (15.00%)
Per model:
|      sum |    count |   failure_rate |
|---------:|---------:|---------------:|
| 135.0000 | 300.0000 |         0.4500 |
|   0.0000 | 300.0000 |         0.0000 |
|   0.0000 | 300.0000 |         0.0000 |
Per strategy:
|     sum |    count |   failure_rate |
|--------:|---------:|---------------:|
| 64.0000 | 450.0000 |         0.1422 |
| 71.0000 | 450.0000 |         0.1578 |
Per language:
|     sum |    count |   failure_rate |
|--------:|---------:|---------------:|
| 46.0000 | 300.0000 |         0.1533 |
|  4.0000 | 300.0000 |         0.0133 |
| 85.0000 | 300.0000 |         0.2833 |
Per model x strategy x language:
|     sum |   count |   failure_rate |
|--------:|--------:|---------------:|
| 24.0000 | 50.0000 |         0.4800 |
|  0.0000 | 50.0000 |         0.0000 |
| 40.0000 | 50.0000 |         0.8000 |
| 22.0000 | 50.0000 |         0.4400 |
|  4.0000 | 50.0000 |         0.0800 |
| 45.0000 | 50.0000 |         0.9000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
|  0.0000 | 50.0000 |         0.0000 |
Error value counts:
| error          |   count |
|:---------------|--------:|
| nan            |     765 |
| empty_response |     135 |

## 3. Accuracy patterns
Overall valid accuracy: 610/765 = 79.74%
Accuracy per strategy (valid-only):
|   sum |   count |   mean |
|------:|--------:|-------:|
|   306 |     386 | 0.7927 |
|   304 |     379 | 0.8021 |
Accuracy per language (valid-only):
|   sum |   count |   mean |
|------:|--------:|-------:|
|   209 |     254 | 0.8228 |
|   292 |     296 | 0.9865 |
|   109 |     215 | 0.5070 |
Accuracy per model (valid-only):
|   sum |   count |   mean |
|------:|--------:|-------:|
|   158 |     165 | 0.9576 |
|   232 |     300 | 0.7733 |
|   220 |     300 | 0.7333 |
Accuracy per model x strategy x language (valid-only):
|   sum |   count |   mean |
|------:|--------:|-------:|
|    24 |      26 | 0.9231 |
|    50 |      50 | 1.0000 |
|    10 |      10 | 1.0000 |
|    24 |      28 | 0.8571 |
|    45 |      46 | 0.9783 |
|     5 |       5 | 1.0000 |
|    44 |      50 | 0.8800 |
|    49 |      50 | 0.9800 |
|    23 |      50 | 0.4600 |
|    39 |      50 | 0.7800 |
|    50 |      50 | 1.0000 |
|    27 |      50 | 0.5400 |
|    39 |      50 | 0.7800 |
|    49 |      50 | 0.9800 |
|    18 |      50 | 0.3600 |
|    39 |      50 | 0.7800 |
|    49 |      50 | 0.9800 |
|    26 |      50 | 0.5200 |
Overall success rate (failures count as wrong):
| model       |   overall_success_rate |
|:------------|-----------------------:|
| gptoss120b  |                 0.5267 |
| llama33-70b |                 0.7733 |
| qwen3-32b   |                 0.7333 |

## 4. Deduplication
Duplicate eval keys (sample_id+strategy+model): 0
Fully duplicate eval rows: 0
Duplicate MCQ keys (sample_id+strategy): 0
Distinct sample_id: s1=150, s2=150, all=150
Sample_id overlap: S1 only 0, S2 only 0, shared 150
s1 duplicate (language,source_proverb) pairs: 0
s2 duplicate (language,source_proverb) pairs: 0
all duplicate (language,source_proverb) pairs: 142

## 5. Data quality
MCQ counts by strategy and language:
| strategy   |   Arabic |   English |   Yoruba |   All |
|:-----------|---------:|----------:|---------:|------:|
| S1         |       50 |        50 |       50 |   150 |
| S2         |       50 |        50 |       50 |   150 |
| All        |      100 |       100 |      100 |   300 |
Fallbacks in S2 by language:
|    sum |   count |   fallback_rate |
|-------:|--------:|----------------:|
| 1.0000 | 50.0000 |          0.0200 |
| 0.0000 | 50.0000 |          0.0000 |
| 6.0000 | 50.0000 |          0.1200 |
Total S2 fallbacks: 7/150 (4.67%)
gen_attempts distribution (S2):
|   gen_attempts |   count |
|---------------:|--------:|
|              1 |     120 |
|              2 |      11 |
|              3 |       6 |
|              4 |       3 |
|              5 |      10 |
gen_info distribution (S2):
| gen_info      |   count |
|:--------------|--------:|
| generated     |     143 |
| hard-fallback |       7 |
MCQs where Answer letter does not map to gold text: 0/300
Distractor counts:
|   dcount |   count |
|---------:|--------:|
|        3 |     300 |
MCQs with distractor_count != 3: 0
MCQs with duplicate choices: 0
MCQs where gold appears in distractors: 0
Predicted values not in A-D: 0

## 6. Pipeline state
```json
{
  "global_key_index": 1122,
  "all_keys_hash": "87e6d08bb148ecedb23f45b60ac693aa",
  "timestamp": "2026-06-09T14:58:11.496710",
  "exhausted": false,
  "message": "",
  "global_consecutive_failures": 0,
  "client_states": {
    "llama33-70b": {
      "delay": 5.0,
      "consecutive_failures": 0,
      "consecutive_successes": 300,
      "total_calls": 300,
      "total_failures": 0
    },
    "gptoss120b": {
      "delay": 5.0,
      "consecutive_failures": 0,
      "consecutive_successes": 300,
      "total_calls": 300,
      "total_failures": 0
    },
    "qwen3-32b": {
      "delay": 5.0,
      "consecutive_failures": 0,
      "consecutive_successes": 522,
      "total_calls": 522,
      "total_failures": 0
    }
  }
}
```
exhausted=False; global_key_index=1122; timestamp=2026-06-09T14:58:11.496710; global_consecutive_failures=0
Client states:
| model       |   delay |   consecutive_failures |   consecutive_successes |   total_calls |   total_failures |
|:------------|--------:|-----------------------:|------------------------:|--------------:|-----------------:|
| llama33-70b |     5.0 |                    0.0 |                   300.0 |         300.0 |              0.0 |
| gptoss120b  |     5.0 |                    0.0 |                   300.0 |         300.0 |              0.0 |
| qwen3-32b   |     5.0 |                    0.0 |                   522.0 |         522.0 |              0.0 |
Evaluation rows per model:
| model       |   eval_rows |
|:------------|------------:|
| llama33-70b |         300 |
| gptoss120b  |         300 |
| qwen3-32b   |         300 |
Note: qwen total_calls (522) exceeds its eval rows (300), indicating qwen was also used for generation.

## 7. Summary stats cross-check
Max absolute difference between summary_stats and recomputed from eval_results:
| metric               |   max_abs_diff |
|:---------------------|---------------:|
| total_n              |       0.000000 |
| valid_n              |       0.000000 |
| failure_n            |       0.000000 |
| failure_rate         |       0.000000 |
| accuracy             |       0.000261 |
| overall_success_rate |       0.000000 |
Recomputed per-group values:
| strategy   | language   | model       |   total_n |   valid_n |   failure_n |   failure_rate |   accuracy |   overall_success_rate |
|:-----------|:-----------|:------------|----------:|----------:|------------:|---------------:|-----------:|-----------------------:|
| S1         | Arabic     | gptoss120b  |   50.0000 |   26.0000 |     24.0000 |         0.4800 |     0.9231 |                 0.4800 |
| S1         | Arabic     | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.8800 |                 0.8800 |
| S1         | Arabic     | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.7800 |                 0.7800 |
| S1         | English    | gptoss120b  |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     1.0000 |                 1.0000 |
| S1         | English    | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.9800 |                 0.9800 |
| S1         | English    | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.9800 |                 0.9800 |
| S1         | Yoruba     | gptoss120b  |   50.0000 |   10.0000 |     40.0000 |         0.8000 |     1.0000 |                 0.2000 |
| S1         | Yoruba     | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.4600 |                 0.4600 |
| S1         | Yoruba     | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.3600 |                 0.3600 |
| S2         | Arabic     | gptoss120b  |   50.0000 |   28.0000 |     22.0000 |         0.4400 |     0.8571 |                 0.4800 |
| S2         | Arabic     | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.7800 |                 0.7800 |
| S2         | Arabic     | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.7800 |                 0.7800 |
| S2         | English    | gptoss120b  |   50.0000 |   46.0000 |      4.0000 |         0.0800 |     0.9783 |                 0.9000 |
| S2         | English    | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     1.0000 |                 1.0000 |
| S2         | English    | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.9800 |                 0.9800 |
| S2         | Yoruba     | gptoss120b  |   50.0000 |    5.0000 |     45.0000 |         0.9000 |     1.0000 |                 0.1000 |
| S2         | Yoruba     | llama33-70b |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.5400 |                 0.5400 |
| S2         | Yoruba     | qwen3-32b   |   50.0000 |   50.0000 |      0.0000 |         0.0000 |     0.5200 |                 0.5200 |
Strategy overall recomputed:
| strategy   |   total_n |   valid_n |   failure_n |   failure_rate |   accuracy |   overall_success_rate |
|:-----------|----------:|----------:|------------:|---------------:|-----------:|-----------------------:|
| S1         |  450.0000 |  386.0000 |     64.0000 |         0.1422 |     0.7927 |                 0.6800 |
| S2         |  450.0000 |  379.0000 |     71.0000 |         0.1578 |     0.8021 |                 0.6756 |
Summary ALL rows:
| strategy   |   total_n |   valid_n |   failure_n |   failure_rate |   accuracy |   overall_success_rate |
|:-----------|----------:|----------:|------------:|---------------:|-----------:|-----------------------:|
| S1         |       450 |       386 |          64 |         0.1420 |     0.7930 |                 0.6800 |
| S2         |       450 |       379 |          71 |         0.1580 |     0.8020 |                 0.6760 |

## 8. Anomalies
MCQs where all 3 models gave same letter: 146/300
  Unanimous and all correct: 145; all wrong: 1
Perfect accuracy groups (model x strategy x language): 4
| model       | strategy   | language   |   match |
|:------------|:-----------|:-----------|--------:|
| gptoss120b  | S1         | English    |  1.0000 |
| gptoss120b  | S1         | Yoruba     |  1.0000 |
| gptoss120b  | S2         | Yoruba     |  1.0000 |
| llama33-70b | S2         | English    |  1.0000 |
Zero accuracy groups (model x strategy x language): 0
gptoss-120b anomaly: high failure rates (Arabic 48%/44%, Yoruba 80%/90% S1/S2) but high accuracy when it responds (S1 0.977, S2 0.937).
Empty raw_response with no error: 0
Valid rows where predicted != raw_response: 300

## 9. Comparison with expected
Expected evaluations: 900 (300 MCQs x 3 models)
Actual evaluations: 900; missing: 0
Previous extracted/ exists: False
No previous extracted/ directory found; comparison not possible.

## 10. Yoruba S2 quality
Fallbacks by language (S2):
|    sum |   count |   fallback_rate |
|-------:|--------:|----------------:|
| 1.0000 | 50.0000 |          0.0200 |
| 0.0000 | 50.0000 |          0.0000 |
| 6.0000 | 50.0000 |          0.1200 |
Yoruba S2 MCQs: 50; fallbacks: 6 (12.00%); generated: 44
Yoruba S2 gen_attempts distribution:
|   gen_attempts |   count |
|---------------:|--------:|
|              1 |      25 |
|              2 |       8 |
|              3 |       5 |
|              4 |       3 |
|              5 |       9 |
Yoruba S2 gen_info distribution:
| gen_info      |   count |
|:--------------|--------:|
| generated     |      44 |
| hard-fallback |       6 |
Yoruba accuracy S1 vs S2 (valid-only):
|   sum |   count |   mean |
|------:|--------:|-------:|
|    51 |     110 | 0.4636 |
|    58 |     105 | 0.5524 |
Yoruba failure rates S1 vs S2:
|     sum |    count |   failure_rate |
|--------:|---------:|---------------:|
| 40.0000 | 150.0000 |         0.2667 |
| 45.0000 | 150.0000 |         0.3000 |
Yoruba S2 per-model valid accuracy:
|   sum |   count |   mean |
|------:|--------:|-------:|
|     5 |       5 | 1.0000 |
|    27 |      50 | 0.5400 |
|    26 |      50 | 0.5200 |

## Appendix: Raw distributions
Predicted letter distribution:
| predicted   |   count |
|:------------|--------:|
| A           |     262 |
| C           |     194 |
| D           |     162 |
| B           |     147 |
| nan         |     135 |
Match distribution:
|   match |   count |
|--------:|--------:|
|       1 |     610 |
|       0 |     155 |
|     nan |     135 |
Language x strategy counts in eval_results:
| language   |   S1 |   S2 |   All |
|:-----------|-----:|-----:|------:|
| Arabic     |  150 |  150 |   300 |
| English    |  150 |  150 |   300 |
| Yoruba     |  150 |  150 |   300 |
| All        |  450 |  450 |   900 |