"""
Convert openrouter_pilot_distractor_generation_test_nano_opus.py into a
self-contained Kaggle notebook (.ipynb). The prompt-variant JSON is embedded
as base64 so there are no triple-quote or escaping issues.

This version adds Markdown cells that highlight the important stages from
start to finish, so the notebook is readable in the Kaggle UI without needing
to scroll through the entire code cell.
"""

import base64
import os
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

NOTEBOOK_NAME = "openrouter_pilot_distractor_generation_test_nano_opus.ipynb"
SRC_NAME = "openrouter_pilot_distractor_generation_test_nano_opus.py"
JSON_NAME = "pilot1_prompt_variants.json"


OVERVIEW_MD = """# 🧪 Pilot 1 TEST — Multi-Model Distractor Shakedown

**Goal:** Low-cost shakedown of the distractor-generation and blind-audit pipeline before scaling up.

**What happens, start to finish:**

1. **Cell 1 (below)** — Reconstructs the 4 prompt-variant JSON file from an embedded base64 payload. No separate JSON upload is needed.
2. **Cell 2** — Loads the full Python source: config, OpenRouter client, data loader, prompt variants, generation/audit logic, preflight checks, and the main pipeline.
3. **Cell 3** — Runs `main()`. This is where the API calls happen:
   - **Preflight** (before any big spend): checks the live OpenRouter catalog, probes every generator and auditor with a tiny prompt, and estimates the total cost.
   - **Generation**: each sampled proverb is run through up to 6 generators × 4 prompt variants. With `N_PER_LANG = 1` this is ~72 MCQs (fewer if some variants/generators are benched).
   - **Blind audit**: each MCQ is shown to 4 auditors without the proverb or correct meaning.
   - **Results**: CSVs, PNG figures, and a JSON summary are written to `/kaggle/working/openrouter_pilot1_test_output/`.

**Hard guardrails:**
- `$5.00` cost cap enforced by `CostTracker.would_exceed()` on every call.
- `MAX_TOKENS_GEN = 2048` — high enough to complete a JSON array of 4 meanings, avoiding truncation while staying inside context limits.
- `MAX_TOKENS_AUDIT = 256` — enough room for short-answer auditors.
- 400/422 fallback strategies retry without `max_tokens` or JSON mode.
- Post-parse filters: generic-English idiom blocklist, correct-meaning leak filter (language-specific threshold), duplicate repair, NLI paraphrase filter, semantic-distance band, offensive-content fallback guard.
- Yoruba hardening: cultural-context prompt injection + blocklist for generic English idioms + LLM curation of literal glosses.

**Expected spend:** ~$0.20–$0.40 for `N_PER_LANG = 1` (well under the cap).
"""


SOURCE_MD = """## ⚙️ Cell 2 — Load code

This cell defines everything needed by the pipeline:
- `GENERATOR_POOL` (starters): `qwen/qwen3.7-max`, `google/gemma-4-31b-it`, `google/gemini-2.5-flash`
- `AUDIT_COMMITTEE` (starters): `meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-small-3.2-24b-instruct`, `google/gemma-3-27b-it`, `deepseek/deepseek-v3.2`
- `CRITIC_MODEL` (self-critique): currently DISABLED (`USE_SELF_CRITIQUE = False`) because it triggered rewrites without improving shortcut-resistance.
- `openrouter_chat()`: retry + 400/422 fallback logic
- `generate_options()`: prompt-variant generation, JSON parsing, length fallback, meta-text/idiom/leak/NLI filters, duplicate repair
- `audit_one_mcq()`: blind A-D vote extraction; optional with-proverb baseline
- `preflight_check()`: live-catalog / connectivity / cost-envelope check
- `main()`: orchestrates sampling, generation, audit, and output saving
"""


RUN_MD = """## 🚀 Cell 3 — Run the pipeline

When you run this cell, the notebook will:
1. Load the 3 cleaned CSVs (English / Arabic / Yoruba).
2. Sample `N_PER_LANG = 1` proverb per language (3 total).
3. **Preflight** — verify API key, live model catalog, probe every model, and abort if the cost estimate is too high.
4. Generate MCQs with 3 active generators and all 4 prompt variants (36 MCQs total).
5. Run the 4-model blind audit on every MCQ.
6. Apply post-generation filters (idiom blocklist, leak filter, NLI paraphrase filter, duplicate repair).
7. Self-critique is disabled; generation runs once per (generator, variant, proverb) to reduce cost and meta-text leakage.
8. Save results, figures, distractor-quality metrics, and print per-generator / per-variant consensus accuracy.

> **Watch the output.** If the preflight probes fail, stop here and check the API key / model names before re-running.
> **Do not change `N_PER_LANG` above 1 until the quality gates in `AGENTS.md` are met.**
"""


AFTER_MD = """## ✅ After execution

Check the output directory for forensics:

- `pilot1_test_generated_mcqs.csv` — every MCQ with generator, variant, options, and generation status
- `pilot1_test_audit_results.csv` — raw votes and consensus per MCQ
- `pilot1_test_prompt_comparison.csv` — per-generator/variant/language consensus accuracy
- `pilot1_test_raw_outputs.csv` — full raw model outputs for debugging response-shape issues
- `pilot1_test_distractor_metrics.csv` — conventional distractor-quality statistics
- `pilot1_test_human_annotation_sample.csv` — stratified spot-check sample for human annotators
- `pilot1_test_summary.json` — full run summary + cost history

**Key diagnostics:**
- In `pilot1_test_raw_outputs.csv`, filter `stage == 'generation'` and check `raw_model_output` is non-empty.
- In `pilot1_test_audit_results.csv`, confirm all 4 auditors contribute votes.
- In `pilot1_test_summary.json`, verify actual cost vs the `$5.00` cap and check `validation_issues`.
- In `pilot1_test_generated_mcqs.csv`, check that `duplicate_options` is `False` and keys are balanced.
"""


def main():
    if not os.path.exists(SRC_NAME):
        raise FileNotFoundError(f"{SRC_NAME} not found")
    if not os.path.exists(JSON_NAME):
        raise FileNotFoundError(f"{JSON_NAME} not found. Run update_prompt_variants.py first.")

    with open(SRC_NAME, encoding="utf-8") as f:
        src = f.read()

    with open(JSON_NAME, encoding="utf-8") as f:
        variants_json = f.read()

    encoded = base64.b64encode(variants_json.encode("utf-8")).decode("ascii")

    cells = []

    # Overview
    cells.append(new_markdown_cell(OVERVIEW_MD))

    # Cell 1: reconstruct the JSON file in the Kaggle working directory.
    cells.append(new_code_cell(
        "# Cell 1: Re-create the prompt-variant catalog from the embedded base64 payload\n"
        "import base64\n"
        f"PROMPT_VARIANTS_B64 = \"\"\"{encoded}\"\"\"\n"
        "with open('pilot1_prompt_variants.json', 'wb') as f:\n"
        "    f.write(base64.b64decode(PROMPT_VARIANTS_B64))\n"
        "print('Prompt variants JSON ready')"
    ))

    # Source-load marker
    cells.append(new_markdown_cell(SOURCE_MD))

    # Cell 2: main source. Replace __main__ guard; main() is called in cell 3.
    src = src.replace('if __name__ == "__main__":\n    main()\n', '')
    cells.append(new_code_cell(src))

    # Run marker
    cells.append(new_markdown_cell(RUN_MD))

    # Cell 3: execute.
    cells.append(new_code_cell("main()"))

    # After-execution marker
    cells.append(new_markdown_cell(AFTER_MD))

    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }

    # Validate
    nbformat.validate(nb)

    with open(NOTEBOOK_NAME, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"Wrote {NOTEBOOK_NAME}")
    print(f"Notebook has {len(nb.cells)} cells ({sum(1 for c in nb.cells if c.cell_type == 'markdown')} markdown, {sum(1 for c in nb.cells if c.cell_type == 'code')} code)")


if __name__ == "__main__":
    main()
