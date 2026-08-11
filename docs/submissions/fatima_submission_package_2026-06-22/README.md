# Fatima Fellowship Submission Package — 2026-06-22

This folder contains everything needed for the OpenRouter quota request, plus a LaTeX stub for easy upload to Overleaf.

## Files

- `ProverbGap_State_of_Work_2026-06-22.docx` — the 2-page state-of-work document to submit.
- `figures/` — high-resolution PNG figures used in the DOCX, renamed for clarity.
  - `fig1_per_language_consensus_accuracy.png` — consensus accuracy by language (v68, N=5).
  - `fig2_generation_status_and_repairs.png` — generation status distribution and mean repairs per MCQ.
  - `fig3_generator_variant_accuracy_heatmap.png` — generator × variant accuracy heatmap (v68).
  - `fig4_failure_mode_summary.png` — failure-mode taxonomy summary (v58–v68).
- `latex_for_overleaf/` — Overleaf-ready LaTeX version of the DOCX content. It already includes a copy of the figures in `latex_for_overleaf/figures/`, so you can zip this folder and upload it directly.

## Quick Overleaf upload

1. Zip the `latex_for_overleaf/` folder.
2. Upload the zip to Overleaf.
3. Compile `main.tex`.

## DOCX figures → LaTeX figure mapping

| DOCX figure | LaTeX file | Caption |
|---|---|---|
| Figure 1 | `fig1_per_language_consensus_accuracy.png` | Consensus accuracy by language (v68, N=5). English is easiest; Arabic and Yoruba are near random, showing the distractors are hard. |
| Figure 2 | `fig2_generation_status_and_repairs.png` | Generation status and mean repairs per MCQ. 44\% of items needed fallback repairs; NLI/leak filters are the main drivers. |
| Figure 3 | `fig3_generator_variant_accuracy_heatmap.png` | Generator × variant accuracy heatmap (v68). Performance varies by model and prompting strategy. |
| Figure 4 | `fig4_failure_mode_summary.png` | Failure modes documented across v58–v68. Each is a reproducible pipeline weakness we treat as a contribution. |
