# ProverbGap MCQ

> **Shortcut-resistant multiple-choice questions for proverb understanding across English, Arabic, and Yoruba.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](#license)

## Live Annotation App

**Try it now:** https://annotationapp.vercel.app

The annotation app is live and accepting responses. Native speakers of English, Arabic, and Yoruba can annotate directly in the browser—no installation required.

---

## Current Status

**v68 production dataset is complete.** We have 180 MCQs ($0.85 generation cost, N=5 per language) validated on Kaggle. Human validation is the next milestone.

| Milestone | Status |
|-----------|--------|
| v68 dataset generation (180 MCQs) | ? Complete |
| Kaggle N=5 validation run | ? Complete |
| Blind audit pipeline | ? Complete |
| Annotation app deployed | ? Live at `https://annotationapp.vercel.app` |
| Supabase DB provisioned (62 items) | ? Live |
| E2E tests (Playwright) | ? Passing |
| Shortcut-audit UI removed | ? Complete |
| Secret rotation / cleanup | ? Complete |
| Docs + community files | ? Complete |
| 60-item human validation | ?? Ready to launch |
| Branch protection on `main` | ? Manual step required |

**Where we stopped:** The annotation app is production-ready and deployed. We removed the shortcut-audit UI from the annotator interface to reduce burden; those fields remain in the database for future research. The next step is recruiting 9 native-speaker annotators (3 per language × 20 items each) to achieve Fleiss' Kappa ? 0.6.

---

## What is ProverbGap?

ProverbGap is a research project that builds **hard multiple-choice questions (MCQs)** to test whether AI models truly understand proverbs—or if they're just cheating by spotting surface-level patterns. We generate questions in **English, Arabic, and Yoruba**, run them through a rigorous audit pipeline, and then have native speakers validate the hardest items.

**Why does this matter?** Modern AI can score 90%+ on simple proverb tests, but often by exploiting shortcuts like "the longest answer is probably right" or "answers that repeat words from the proverb are usually correct." ProverbGap creates questions that close those shortcuts, giving us a more honest measure of AI comprehension.

**Who is this for?** Researchers benchmarking LLMs, developers building better evaluation datasets, and native speakers who want to contribute culturally authentic validation data.

---

## Quick Start

Choose the path that matches what you want to do:

### I want to annotate (human validation)

The annotation app lets you review MCQs in a browser. No code experience needed.

```bash
# 1. Clone the repo
git clone https://github.com/saaga23/proverb_mcq.git
cd proverb_mcq

# 2. Set up the annotation app
cd annotation_app
cp .env.example .env.local
# Edit .env.local with your Supabase credentials (see Prerequisites below)
npm install
npm run setup-db   # Creates database tables
npm run dev
```

Open `http://localhost:3000` and start annotating.

See [annotation_app/ANNOTATOR_ONBOARDING.md](annotation_app/ANNOTATOR_ONBOARDING.md) for the annotator guide.

### I want to contribute code

You'll need Python, Node.js, and a Supabase account.

```bash
# 1. Clone and enter
git clone https://github.com/saaga23/proverb_mcq.git
cd proverb_mcq

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run tests
pytest tests/ -v

# 4. (Optional) Run the annotation app locally
cd annotation_app
cp .env.example .env.local
# Fill in Supabase credentials
npm install
npm run setup-db
npm run dev
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for code style, commit conventions, and the PR process.

### I want to understand the research

Start with these files in order:

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** — Plain-English explanation of proverbs, distractors, and the full pipeline.
2. **[DATASET_CARD.md](DATASET_CARD.md)** — What's in the data, how it was collected, and known limitations.
3. **[annotation/protocol.md](annotation/protocol.md)** — The human-validation protocol, rubric, and quality controls.
4. **[docs/Elite_Research_Execution_Plan.md](docs/Elite_Research_Execution_Plan.md)** — Research methodology and rigor standards.
5. **[annotation_app/README.md](annotation_app/README.md)** — Annotation app architecture and deployment.

---

## Prerequisites

| Tool | Version | Why You Need It |
|------|---------|-----------------|
| **Python** | 3.10+ | Runs the generation, audit, and analysis pipeline |
| **Node.js** | 22.x | Required by Next.js 16 for the annotation app |
| **npm** | 10+ (comes with Node.js) | Installs annotation app dependencies |
| **Supabase** | Free tier works | Backend database for annotation storage and concurrency |
| **Vercel** | Free tier works | Deploys the annotation app (optional, for sharing) |
| **OpenRouter API key** | Pay-as-you-go | Runs LLM generation/audit (only for pipeline, not annotation) |

> **Tip:** If you only want to annotate or read docs, you only need Node.js and a Supabase account. Skip Python and OpenRouter.

---

## How the Project Works

```
????????????????    ????????????????    ????????????????    ??????????????????    ????????????????
?    Data      ?????? Generation   ??????    Audit     ??????  Annotation    ??????   Analysis   ?
?  (Proverbs)  ?    ? (Distractors)?    ?  (Blind)     ?    ?   (Humans)     ?    ?   (Stats)    ?
????????????????    ????????????????    ????????????????    ??????????????????    ????????????????
       ?                   ?                  ?                   ?                    ?
       ?                   ?                  ?                   ?                    ?
 raw corpora    LLM generates 4    4 LLMs vote on    Native speakers      Tables,
 (3 languages)  options each      correct answer     rate plausibility     figures,
                 (A-D)             blind (no proverb)  & flag shortcuts      LaTeX
```

1. **Data** — Proverbs from English, Arabic, and Yoruba corpora.
2. **Generation** — LLMs produce 4 multiple-choice options (1 correct meaning + 3 distractors).
3. **Audit** — A separate committee of LLMs votes on the correct answer *without seeing the proverb*.
4. **Annotation** — Native speakers review the hardest items, select correct answers, and provide confidence ratings.
5. **Analysis** — We measure inter-annotator agreement, shortcut resistance, and cross-lingual performance.

---

## Dataset

### v68 Production Dataset

The current production dataset is generated by the **frozen v67 configuration**, validated at **N=5 per language** on Kaggle (15 proverbs total, 180 MCQs).

| Metric | Value |
|--------|-------|
| MCQs generated | **180** |
| Total generation cost | **$0.85** |
| Perfect consensus rate | 41.7% |
| High-consensus-wrong (HCW) | 27.8% |
| Consensus accuracy | 56.7% |
| Partial + fallback | 43.9% |
| Duplicate options | 0% |
| Correct-key balance | 45/45/45/45 |

**Primary data files:**

- `data/production/paper_first_outputs_2026-06-22_10-42-02/` — v68 paper-first outputs, tables, figures, and 60-item human-validation sample
- `kaggle/run_logs/v68/` — Full v68 run logs, analysis scripts, and reproducibility artifacts

### Known Limitations

1. **Corpus fallback sampler is the confirmed bottleneck.** 43.9% of items required fallback replacements; fallbacks are the primary driver of high-consensus-wrong items.
2. **English distractors are too easy.** 65% consensus accuracy and 45% perfect consensus; distractors lack sufficient temptation.
3. **Yoruba is fragile.** Meets the 50% correctness gate only barely (51.7%); cultural and literal-translation issues persist.
4. **HCW remains elevated at 27.8%.** Well above the 10% target; many fallback distractors attract auditor consensus.

---

## Deep Dive: Reading Paths

### For Researchers
1. [GETTING_STARTED.md](GETTING_STARTED.md) — Understand the basics
2. [DATASET_CARD.md](DATASET_CARD.md) — Data provenance and limitations
3. [annotation/protocol.md](annotation/protocol.md) — Human-validation protocol
4. `paper/proverbgap_eacl2027.md` — Full paper draft
5. `kaggle/run_logs/v68/v68_detailed_analysis_report.md` — Latest analysis
6. `docs/Elite_Research_Execution_Plan.md` — Methodology rigor

### For Developers
1. [GETTING_STARTED.md](GETTING_STARTED.md) — Project overview
2. [annotation_app/README.md](annotation_app/README.md) — App architecture
3. `annotation_app/supabase/schema.sql` — Database schema and RPCs
4. `annotation_app/src/components/AnnotationUI.tsx` — Main annotator interface
5. `annotation_app/e2e/annotation.spec.ts` — E2E tests
6. [CONTRIBUTING.md](CONTRIBUTING.md) — Code style and PR process

### For Annotators
1. [annotation_app/ANNOTATOR_ONBOARDING.md](annotation_app/ANNOTATOR_ONBOARDING.md) — Step-by-step guide
2. `annotation/protocol.md` — Full protocol and rubric
3. [annotation_app/README.md](annotation_app/README.md) — How to access the app

### For Reviewers
1. `submission_package_2026-08-02/` — Complete submission package
2. `paper/proverbgap_eacl2027.md` — Paper draft
3. `paper/tables/` — All LaTeX table sources
4. `paper/figures/` — Publication-ready figures
5. `kaggle/run_logs/v68/` — Reproducibility artifacts

---

## Project Structure

```
proverb_mcq/
??? actual_data/                 # Cleaned proverb corpora (3 languages)
?   ??? Arabic_cleaned.csv
?   ??? English_cleaned.csv
?   ??? Yoruba_cleaned.csv
??? annotation/                  # Human-validation tooling
?   ??? protocol.md              # Validation protocol, rubric, IRB
?   ??? blinded_export.py        # Blinding utility for export
?   ??? compute_iaa.py           # Inter-annotator agreement
?   ??? outputs/                 # Annotation outputs and IAA reports
?   ??? tests/                   # Annotation-specific tests
??? annotation_app/              # Next.js + Supabase annotation frontend
?   ??? src/
?   ?   ??? app/
?   ?   ?   ??? page.tsx         # Landing + consent
?   ?   ?   ??? annotate/page.tsx # Annotation interface
?   ?   ?   ??? admin/page.tsx   # Admin dashboard
?   ?   ??? components/
?   ?   ?   ??? AnnotationUI.tsx # Main annotator component
?   ?   ??? lib/
?   ?       ??? supabase.ts      # Typed Supabase client
?   ??? supabase/
?   ?   ??? schema.sql           # Full DB schema + RPCs
?   ?   ??? rpc.sql              # Deprecated (use schema.sql)
?   ?   ??? run_in_dashboard.sql # Manual dashboard SQL
?   ??? scripts/
?   ?   ??? setup_database.ts    # DB setup helper
?   ?   ??? upload_items.ts      # CSV uploader
?   ?   ??? export_annotations.ts # CSV exporter
?   ??? e2e/
?   ?   ??? annotation.spec.ts   # Playwright E2E tests
?   ??? ANNOTATOR_ONBOARDING.md  # Annotator guide
??? data/
?   ??? production/
?       ??? paper_first_outputs_2026-06-22_10-42-02/
?           ??? human_validation_sample_60.csv
?           ??? table*.csv       # Paper tables
??? docs/                        # Methodology and planning docs
??? kaggle/                      # Kaggle automation and run logs
?   ??? run_logs/
?   ?   ??? v68/                 # v68 production run
?   ?   ??? v69/                 # v69 comparison run
?   ??? kaggle_analysis/         # Analysis scripts and reports
??? paper/                       # Paper artifacts
?   ??? proverbgap_eacl2027.md   # Main paper draft
?   ??? sections/                # Individual sections
?   ??? tables/                  # LaTeX table sources
?   ??? figures/                 # Publication-ready figures
??? scripts/                     # Utility scripts
??? src/                         # Python source
?   ??? generation/              # Distractor generation pipeline
?   ??? evaluation/              # S1/S2 evaluator
??? tests/                       # Local pytest suites
??? submission_package_2026-08-02/ # Final submission package
??? .archive/                    # Archived legacy code and outputs
??? CONTRIBUTING.md              # Contributor guide
??? DATASET_CARD.md              # Dataset metadata
??? GETTING_STARTED.md           # Plain-English project intro
??? SECURITY.md                  # Security policy and incident history
??? CHANGELOG.md                 # Version history
??? CODE_OF_CONDUCT.md           # Community standards
??? DATA_PROVENANCE_TEMPLATE.md  # Data provenance tracking
??? PUBLICATION_READINESS_REPORT.md # Publication checklist
??? requirements.txt             # Python dependencies
??? README.md                    # This file
```

---

## Human Validation Protocol

Human validation is conducted on a **60-item stratified sample** drawn from the v68 production dataset. The sample is split **20 items per language** (English, Arabic, Yoruba) and stratified by generation status and consensus correctness to ensure balanced coverage of easy, ambiguous, and failure-mode items.

### Protocol

- **3 native-speaker annotators per item** (9 total annotators across 3 languages; minimum 2 required for IAA computation).
- **Blind options-only protocol:** Annotators see only the proverb text and four options (A–D). Correct answer, LLM consensus labels, and vote columns are hidden.
- **Two-part judgment:** Correct answer selection plus a 5-point distractor plausibility rating per option.
- **Attention checks:** Embedded trap items with obvious correct answers; minimum 80% accuracy required.
- **Timing guards:** Minimum 10 seconds and maximum 120 seconds per item.

### IAA Targets

- **Primary metric:** Fleiss' Kappa for categorical agreement on correct answers.
- **Target:** Kappa ? 0.6 (Good / Publishable quality).
- **Secondary metrics:** Per-language Kappa, item-level agreement, and Spearman correlation of plausibility ratings.

See [annotation/protocol.md](annotation/protocol.md) for the full protocol, rubric, and IRB details.

---

## Annotation App

The human-validation annotation frontend is built with **Next.js 16** and **Supabase**. It supports an **anonymous annotator workflow** (no login required) with **batch-based annotation** delivering **10 items per batch**, embedded **attention checks**, and an **admin dashboard** for CSV export.

### Features

- Anonymous annotator identity via `localStorage`
- Batch-based annotation (10 items per batch)
- Correctness + confidence judgment
- Attention checks embedded in batches
- **Minimum time guard (10 seconds)** to prevent rushing
- Atomic fetch-and-lock via Supabase RPC (`FOR UPDATE SKIP LOCKED`)
- Hidden gold answers (never exposed to browser)
- Time tracking per item
- Optional annotator notes
- Progress tracking
- Admin dashboard for annotation export

See [annotation_app/README.md](annotation_app/README.md) for full setup and deployment instructions.

---

## Pipeline Architecture

### Generation

A **generator** LLM (e.g., `google/gemini-2.5-flash`) is asked to produce 3 distractors given a proverb and its curated gold meaning. The prompt enforces:
- Complete sentences
- Rough length parity with the gold meaning
- No generic idioms or proverb echoes

### Sanitizer Stack

Raw distractors pass through sequential filters:

| Filter | What it checks | Action on failure |
|--------|---------------|-------------------|
| **Length parity** | All options roughly same length | Replace via fallback sampler |
| **Blocklist** | Rejects generic idioms | Replace |
| **Leak guard** | Rejects distractors echoing correct meaning | Replace |
| **Semantic distance** | Rejects distractors too similar to correct answer | Replace |
| **NLI filter** | Rejects paraphrases entailed by correct meaning | Replace |

Failed distractors are replaced by a **fallback sampler** — a curated pool of pre-written distractors from other proverbs.

### Blind Audit

A separate **audit committee** of 4 LLMs votes on the correct answer *without seeing the proverb*. This prevents them from using the proverb text as a shortcut.

If 3 or more auditors agree on a **wrong** answer, that's called a **HCW (High-Consensus-Wrong)** item — a red flag that distractors are tempting but misleading.

---

## Key Findings (v68 N=5)

- **NLI and leak filters dominate rewriter behavior.** Mean 0.36 NLI replacements and 0.35 leak replacements per MCQ; length is only 0.15.
- **`adversarial-hard-negative` is the most damaged variant.** Only 26.7% fully generated, 42.2% length-fallback, 40% HCW.
- **Generator performance varies by model family.** `google/gemma-4-31b-it` was the strongest generator (65% accuracy, 35% HCW, 66.7% fully generated).
- **Roster stability confirmed.** 0 benched generators, 0 missing auditor votes across 180 MCQs.

---

## Security & Privacy

- `.env` and `.env.local` are gitignored. Never commit secrets.
- We previously had an exposed OpenRouter API key in tracked history; it has been deleted and the file purged from git. The key itself should be rotated on the OpenRouter dashboard.
- Supabase `service_role` key is never exposed to the browser; only the `anon` key is public.
- Admin dashboard is client-side password-gated; for production use, add proper authentication.
- Annotator data is anonymous (no PII collected beyond optional demographics).

See [SECURITY.md](SECURITY.md) for the full security policy and incident history.

---

## Troubleshooting

### Python / Pipeline

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` after `pip install` | Make sure your virtual environment is activated: `.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on Mac/Linux |
| `OPENROUTER_API_KEY` not found | Copy `.env.example` to `.env` and add your key. Never commit `.env` to git. |
| Tests fail with connection errors | Some tests mock API calls. Ensure you're running `pytest tests/` from the repo root, not from inside a subdirectory. |

### Annotation App

| Problem | Solution |
|---------|----------|
| `Error: Cannot find module '@supabase/supabase-js'` | Run `npm install` inside `annotation_app/`. |
| Supabase connection refused | Double-check `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env.local`. Make sure the schema.sql has been run in the Supabase SQL Editor. |
| "No items available" | Upload items first: `npm run upload-items` (requires `human_validation_sample_60.csv` in the repo root). |
| Vercel build fails | Ensure Node.js 22 is selected in Vercel settings. Check that all environment variables are set in the Vercel dashboard. |
| Playwright tests timeout | Install browser binaries: `npx playwright install chromium`. |

---

## Paper Artifacts

All paper tables, figures, and LaTeX sources are in `paper/`:

- `paper/proverbgap_eacl2027.md` — Main paper draft (Markdown)
- `paper/figures/` — Publication-ready figures
- `paper/tables/` — LaTeX table sources
- `paper/sections/` — Individual section drafts

### Target Venue

EACL 2027 ARR (ACL Rolling Review).

### Planned Scope

1. **Methodology:** Hardened dynamic-generator + blind options-only audit pipeline for shortcut-resistant distractor generation.
2. **Cross-lingual findings:** S1 vs S2 difficulty, per-language gaps (especially Yoruba), position bias, model-family exploitation.
3. **Reproducible failure taxonomy:** Partial+fallback, high-consensus-wrong, length/leak/NLI replacements, corpus fallback limitations.
4. **Human validation:** 60-item subset (20 per language) with 2–3 native-speaker annotators; IAA reported.

---

## Citation

```bibtex
@misc{abraham2026proverbgap,
  title        = {ProverbGap: Shortcut-Resistant Multiple-Choice Distractors for Proverb Understanding Across English, Arabic, and Yoruba},
  author       = {Abraham, Sunday Aspita},
  year         = {2026},
  howpublished = {arXiv preprint},
  note         = {v68 N=5 production dataset; EACL 2027 ARR submission},
  url          = {https://arxiv.org/abs/XXXX.XXXXX}
}
```

Replace `XXXX.XXXXX` with the actual arXiv identifier upon submission.

---

## License

This project is released under the [MIT License](LICENSE). See `LICENSE` for details.

## Contributing

We welcome contributions from researchers, developers, and native speakers. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code style guidelines, commit conventions, and our PR checklist.

---

*Generated for the ProverbGap research project. For questions, open an issue or contact the maintainers.*
