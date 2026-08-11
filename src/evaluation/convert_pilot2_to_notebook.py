"""
Convert openrouter_pilot_s1_s2_evaluator_v3.py into a Kaggle notebook (.ipynb).
"""

import os
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

NOTEBOOK_NAME = "openrouter_pilot_s1_s2_evaluator.ipynb"
SRC_NAME = "openrouter_pilot_s1_s2_evaluator_v3.py"


def main():
    if not os.path.exists(SRC_NAME):
        raise FileNotFoundError(f"{SRC_NAME} not found")

    with open(SRC_NAME, encoding="utf-8") as f:
        src = f.read()

    # Remove __main__ guard; call main explicitly in the last cell.
    src = src.replace('if __name__ == "__main__":\n    main()\n', '')

    intro = new_markdown_cell(
        "# ProverbGap OpenRouter Pilot 2 v3: Fresh S1 & S2 MCQ Generation + Dynamic Audit\n\n"
        "Regenerates fresh Strategy-1 and Strategy-2 MCQs from the raw cleaned proverbs, "
        "then audits them with a dynamic OpenRouter committee.\n\n"
        "- **S1**: proverb → 4 English meanings\n"
        "- **S2**: meaning → 4 source-language proverbs\n\n"
        "Hardening vs v2:\n"
        "- Dynamic, disjoint generator and audit model pools with football-style substitutions.\n"
        "- Live OpenRouter catalog filtering and cheap echo preflight probes.\n"
        "- Hardened `openrouter_chat` with 400/422 fallbacks and reasoning-family token limits.\n"
        "- CostTracker with live price refresh and a $5 hard cap.\n"
        "- Meta-text rejection, length parity, duplicate detection, and corpus-based fallbacks.\n"
        "- Optional sentence-transformer semantic paraphrase guard for S1.\n\n"
        "Outputs: `mcqs_s1.csv`, `mcqs_s2.csv`, `pilot2_eval_results.csv`, `pilot2_summary.json`, "
        "`pilot2_state.json`, `pilot2_raw_outputs.csv`."
    )
    cell1 = new_code_cell("!pip install -q requests pandas numpy sentence-transformers")
    cell2 = new_code_cell(src)
    cell3 = new_code_cell("main()")

    nb = new_notebook(cells=[intro, cell1, cell2, cell3])
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nbformat.validate(nb)

    with open(NOTEBOOK_NAME, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"Wrote {NOTEBOOK_NAME}")


if __name__ == "__main__":
    main()
