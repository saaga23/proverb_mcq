# ProverbGap: 7-Day Execution Plan
## EACL 2027 ARR Submission + arXiv Dataset Release

**Deadline:** August 3, 2026 (EACL ARR)  
**Sprint:** One intensive week  
**Team:** Abraham (Lead, Writing), Yanmife (Generation/Results), Iremide (FiB/Dataset)  
**Budget:** ~$500 (reserved for post-submission reviewer response, NOT spent this week)  
**Constraint:** No human validation completed; free-tier APIs only; no new large-scale experiments.

---

## Strategic Decisions (Locked for the Week)

| Decision | Rationale |
|----------|-----------|
| **Paper 1 (EACL Findings, 4 pages):** Uses existing N=150 pilot (50/language) results only. | Running N=700 evaluation on free-tier APIs in 7 days is impossible. The methodology contribution does not require scale. |
| **Paper 2 (arXiv + ACL DPI):** Releases full 7,172-proverb collection + 150 MCQs as proof-of-concept. | The dataset paper's contribution is the curated multilingual resource, not the evaluated benchmark. |
| **No new API experiments.** | Risk of API failures, rate limits, and corrupted results is too high with 7 days left. |
| **Honest framing about human validation.** | Both papers explicitly state validation is planned/in-progress. Paper 1 avoids benchmark-validity claims entirely. |
| **Overleaf for both papers.** | Shared, real-time, zero LaTeX environment setup time. |

---

## Pre-Sprint Checklist (Complete Before Day 1)

- [ ] Abraham creates two Overleaf projects and shares links with team
- [ ] Yanmife confirms all N=50 CSVs are intact: `local_test_output_v4/evaluation_results_n50.csv`, `local_test_output_v4/mcqs_s1_n50.csv`, `local_test_output_v4/mcqs_s2_n50.csv`
- [ ] Iremide confirms HuggingFace account access and `datasets` library installed
- [ ] All: Read `docs/ProverbGap_Reframed_Title_Abstract.md` and `neurips_review/EACL_2027_SYNTHESIS.md`

---

## Day 1 (Saturday): Foundation & Truth Audit

### Morning: 2-Hour Team Sync (All Hands)
**Location:** Video call / shared screen

1. Abraham walks through the 4-page Paper 1 outline (section by section, word budget).
2. Yanmife presents the MASTER_RESULTS spreadsheet.
3. Iremide presents the data provenance status and gaps.
4. Lock the scope: No new experiments. No scope creep.

### Afternoon: Parallel Workstreams

**Abraham**
- Create directory structure:
  ```
  papers/
  ├── eacl2027_findings/
  │   ├── main.tex
  │   ├── references.bib
  │   ├── acl_natbib.bst
  │   └── figures/
  └── acl_dpi/
      ├── main.tex
      ├── references.bib
      ├── acl_natbib.bst
      └── figures/
  ```
- Set up both Overleaf projects with ACL 2024 4-page template (Paper 1) and ACL DPI template (Paper 2).
- Draft Paper 1 section outline as LaTeX comments in `main.tex`.

**Yanmife**
- Create `results/MASTER_RESULTS.json` — a single source of truth for every number appearing in either paper.
- Trace every statistic in `docs/ProverbGap_Paper_Draft.md` back to its CSV origin.
- Flag ANY number that cannot be verified. If unverified, it does NOT go in the paper.
- Create `results/NUMBER_AUDIT_LOG.md` documenting the CSV → table → paper chain for each statistic.

**Iremide**
- Complete `DATA_PROVENANCE.md` (copy from `DATA_PROVENANCE_TEMPLATE.md` and fill ALL blanks):
  - **Yoruba:** Cite Owomoyela (2005). State "OCR'd from personal copy; proverbs are traditional knowledge, compilation is copyrighted and cited."
  - **English:** Document as "Aggregated from public-domain proverb compilations (Project Gutenberg, traditional reference works). No single proprietary source."
  - **Arabic:** Find the EXACT HuggingFace dataset ID used. Cite it with license. If unknown, flag as BLOCKER.
- Create `ETHICS_STATEMENT.md` (200 words) covering communal cultural property, intended use, and planned validation.
- If Arabic source is unidentifiable: Abraham decides whether to exclude Arabic from Paper 2 or to flag it honestly as "source under documentation."

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| Overleaf projects live + shared | Abraham | Overleaf URLs in `papers/README.md` |
| `results/MASTER_RESULTS.json` | Yanmife | `results/MASTER_RESULTS.json` |
| `results/NUMBER_AUDIT_LOG.md` | Yanmife | `results/NUMBER_AUDIT_LOG.md` |
| Complete `DATA_PROVENANCE.md` | Iremide | `DATA_PROVENANCE.md` |
| `ETHICS_STATEMENT.md` | Iremide | `ETHICS_STATEMENT.md` |

### GO / NO-GO Checkpoint

- [ ] **GO:** Every number in Paper 1 can be traced to a CSV cell. If NO: Stop. Fix before Day 2.
- [ ] **GO:** Data provenance is complete enough that a reviewer cannot desk-reject for missing sources. If NO: Arabic source must be identified or reframed by end of Day 1.
- [ ] **GO:** Overleaf compiles a blank template without errors. If NO: Fix LaTeX packages immediately.

### Risk Mitigation (Day 1)

| Risk | Mitigation |
|------|------------|
| Unverifiable numbers in draft | Yanmife flags them; Abraham decides to cut or re-run local encoder baseline. |
| Arabic source undocumented | Iremide searches `actual_data/` metadata and `inventory.json`. If still unknown, Abraham reframes Arabic as "pilot subset from open classical collections" and moves full attribution to post-submission fix. |
| Team misalignment on 4-page scope | Abraham enforces word budget during sync: Intro 150 words, Related Work 200, Method 300, Results 200, Negative Results 400, Discussion 100, Conclusion 100 = ~1,450 words + tables/figures ≈ 4 pages. |

---

## Day 2 (Sunday): HuggingFace Release & Paper Skeletons

### Morning

**Abraham**
- Write Paper 1 Abstract (150 words) and Introduction draft in Overleaf.
- Write Paper 2 Abstract and Introduction draft in Overleaf.
- Create shared `references.bib` with 20 core citations pulled from `docs/ProverbGap_Paper_Draft.md`.

**Yanmife**
- Generate all LaTeX tables for Paper 1:
  - Table 1: Benchmark comparison (ProverbEval vs Jawaher vs PRONE vs ProverbGap)
  - Table 2: Primary accuracy results (S1 vs S2 strict vs S2 fallback)
  - Table 3: Per-language breakdown
  - Table 4: Per-model breakdown
  - Table 5: Failure-mode taxonomy (the star table)
- Generate all Paper 1 figures as publication-quality PDFs (if existing PNGs are low-res, regenerate from scripts):
  - Copy/re-export from `Busayou_Package/03_Results_and_Figures/figures/` or `mentor_package/`
  - Ensure ≥300 DPI, fonts embedded

**Iremide**
- Prepare HuggingFace upload package in `huggingface_release/`:
  ```
  huggingface_release/
  ├── README.md          (ACL DPI-compliant dataset card)
  ├── dataset_infos.json
  ├── proverbgap.py      (loading script)
  ├── data/
  │   ├── english_cleaned.csv
  │   ├── arabic_cleaned.csv
  │   └── yoruba_cleaned.csv
  └── mcq_pilot/
      ├── mcqs_s1_n50.csv
      └── mcqs_s2_n50.csv
  ```
- Draft dataset card sections: Description, Collection, Structure, Splits, Licensing, Ethics, Citation, Maintenance.

### Afternoon

**Abraham**
- Review Paper 1 intro with Yanmife for technical accuracy.
- Review Paper 2 intro with Iremide for dataset completeness.

**Yanmife**
- Write Paper 1 Methodology section in Overleaf (0.75 pages max):
  - S1: Negative sampling (2 sentences)
  - S2: Cross-family paraphrasing (4 sentences)
  - Dual-gate validation (3 sentences)
  - Committee evaluation (3 sentences)
  - Position bias mitigation (2 sentences)
  - Statistical tests (2 sentences)
- Create `figures/Figure1_pipeline.pdf` — a clean schematic of generation → gates → committee.

**Iremide**
- Upload to HuggingFace Hub. Test:
  ```python
  from datasets import load_dataset
  ds = load_dataset("username/proverbgap")
  assert len(ds["train"]) == 7172
  ```
- Fix any loading errors.
- Write Paper 2 "Dataset Description" and "Collection Methodology" sections.

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| Paper 1 Abstract + Intro drafted | Abraham | Overleaf |
| Paper 1 Methodology drafted | Yanmife | Overleaf |
| Paper 1 Tables 1-5 in LaTeX | Yanmife | Overleaf + `papers/eacl2027_findings/tables/` |
| Paper 1 Figures 1-6 ready | Yanmife | `papers/eacl2027_findings/figures/` |
| HuggingFace dataset LIVE | Iremide | `https://huggingface.co/datasets/...` |
| Dataset card ≥80% complete | Iremide | `huggingface_release/README.md` |
| Paper 2 Intro + Dataset Desc drafted | Abraham + Iremide | Overleaf |

### GO / NO-GO Checkpoint

- [ ] **GO:** HuggingFace `load_dataset()` succeeds without errors. If NO: Fix until it works. Dataset release is Paper 2's anchor.
- [ ] **GO:** Paper 1 methodology section is ≤0.75 pages. If NO: Cut sub-sections. Move details to appendix.
- [ ] **GO:** All Paper 1 figures are ≥300 DPI. If NO: Regenerate from matplotlib source code.

### Risk Mitigation (Day 2)

| Risk | Mitigation |
|------|------------|
| HuggingFace upload fails (large files) | Iremide uses `git lfs` or the Hub web UI. CSVs are <1MB each; should be fine. |
| Existing figures are low-resolution | Yanmife has source code in `Busayou_Package/05_Source_Code/proverbgap_kaggle_final.ipynb` or similar. Regenerate with `plt.savefig(..., dpi=300)`. |
| Paper 1 Methodology section too long | Abraham enforces hard limit: If it exceeds 0.75 pages, move gate thresholds and prompt details to a 1-page appendix. ARR allows appendices. |

---

## Day 3 (Monday): Paper 1 Core Writing Sprint

**Goal:** Paper 1 complete first draft by 23:59. This is the hardest day.

### Morning (4 hours)

**Abraham: Paper 1 — Related Work + Negative Results (core)**
- Related Work (0.5 pages): 3 paragraphs — (a) Proverb benchmarks, (b) Distractor generation, (c) Same-family exploitation & shortcut learning.
- **Negative Results section (1 page — THE PAPER'S HEART):**
  - Failure 1: Same-family exploitation (+31.1 pp)
  - Failure 2: CoT collapse (82.7% → 48%)
  - Failure 3: MSP triviality (100% acc, 0% fallback)
  - Failure 4: Position bias (p < 0.0001, A-pos 85.6%)
  - Failure 5: API fragility (90%+ failure rates)
  - Failure 6: Memorization signatures (Allam-2-7b: 98.4% → 74.9%)
  - Each failure gets 3-4 sentences: observation, magnitude, implication.

**Yanmife: Paper 1 — Results + Experimental Setup**
- Experimental Setup (0.5 pages): Language coverage, model committee, prompting styles, encoder baselines, statistical tests.
- Results (0.5 pages): Primary accuracy, per-language, per-model, per-style, encoder baselines.
- Ensure every number matches `MASTER_RESULTS.json` exactly.

**Iremide: Paper 1 — Discussion, Limitations, Conclusion**
- Discussion (0.25 pages): Cross-lingual boundary (English 8.9pp S2 drop vs Arabic/Yoruba 2.2pp).
- Limitations (0.25 pages): MCQ-only by design (controlled testbed), no human validation yet, 2-model committee due to API fragility, pilot scale.
- Conclusion (0.25 pages): Summary + future work (FiB, human validation, expanded committee).

### Afternoon (4 hours)

**All: Assembly & Crisis Management**
- Abraham compiles all sections in Overleaf.
- Page count check. If >5 pages: emergency triage.
  - Cut order: (1) Related Work details, (2) Methodology sub-sections, (3) Results per-style breakdown.
  - NEVER cut: Negative Results, Abstract, Limitations.
- Yanmife verifies every number one final time.
- Iremide checks figure captions, table formatting, and citation consistency.

### Evening (2 hours)

- Abraham writes the final Paper 1 abstract (if not already done).
- All: Read Paper 1 aloud. Fix awkward sentences.
- Save as `paper1_draft_v1.pdf`.

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| Paper 1 complete first draft (target ≤4.5 pages) | Abraham | Overleaf PDF |
| Every number verified against CSV | Yanmife | `results/NUMBER_AUDIT_LOG.md` (signed off) |
| All figures/captions correct | Iremide | Overleaf |

### GO / NO-GO Checkpoint

- [ ] **GO:** Paper 1 draft exists and compiles. If NO: Work until midnight. This is non-negotiable.
- [ ] **GO:** Negative Results section is ≥1 page and is the longest single section. If NO: The paper has no contribution. Revise immediately.
- [ ] **GO:** Limitations explicitly state "no human validation" and "pilot scale." If NO: Add now. Hiding this is fatal.

### Risk Mitigation (Day 3)

| Risk | Mitigation |
|------|------------|
| Draft exceeds 5 pages | Abraham has pre-planned cuts: Related Work → 3 citations only; Method → move prompts to appendix; Results → fold per-style into a single sentence. |
| Negative results are boring / unsupported | Each failure MUST have a number and a CSV source. If a failure lacks data, cut it. Keep only the 6 failures with solid evidence. |
| Team burnout | Abraham orders dinner for the team. 30-min break at 6 PM. No one works past midnight. |

---

## Day 4 (Tuesday): Paper 1 Finalization + Paper 2 Acceleration

### Morning (4 hours)

**Abraham: Paper 1 Polish**
- Trim Paper 1 to exactly 4 pages (including references).
- Polish abstract to 150 words.
- Write a compelling first sentence of the introduction.
- Ensure the contribution statement is crystal clear: "We present a failure taxonomy, not a benchmark."

**Yanmife: Paper 2 — Baselines & Evaluation Section**
- Write Paper 2 section on "Demonstrated Application: MCQ Construction":
  - Describe S1/S2 pipeline at high level.
  - Present N=50 results as proof-of-concept.
  - Include encoder baselines and API committee results.
- Create Paper 2 figures:
  - Figure 1: Language distribution pie chart (EN 2278, AR 913, YO 3971)
  - Figure 2: Data structure diagram (what columns exist per language)

**Iremide: Paper 2 — Dataset Quality & Maintenance**
- Write "Known Limitations" section (honest about size imbalance, dialectal homogeneity, no human validation).
- Write "Maintenance & Future Work" section (planned validation, community contributions, versioning).
- Complete HuggingFace dataset card. Ensure it passes the ACL DPI checklist.

### Afternoon (4 hours)

**Abraham: Paper 2 — Compilation**
- Assemble Paper 2 sections: Abstract, Intro, Related Work, Dataset Description, Collection, Structure, Application (MCQ), Baselines, Discussion, Ethics, Conclusion.
- Ensure Paper 2 references the HuggingFace dataset URL.

**Yanmife: Cross-Paper Technical Audit**
- Verify that Paper 1 and Paper 2 do not contradict each other.
- Verify that dataset statistics in Paper 2 match actual CSV row counts (`wc -l actual_data/cleaned/*.csv`).
- Create a shared `references.bib` with no duplicates, no missing fields.

**Iremide: arXiv Prep**
- Create `papers/acl_dpi/arxiv_source.zip` structure.
- Ensure all figures are included and paths are correct.

### Evening (2 hours)

- All: Read Paper 1 again. It should now be "pretty good."
- Abraham: Save `paper1_draft_v2.pdf` as "complete draft."

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| Paper 1 at exactly 4 pages | Abraham | Overleaf PDF |
| Paper 2 complete first draft (6-8 pages) | Abraham | Overleaf PDF |
| Shared `references.bib` complete | Yanmife | `papers/references.bib` |
| arXiv source structure ready | Iremide | `papers/acl_dpi/` |

### GO / NO-GO Checkpoint

- [ ] **GO:** Paper 1 is ≤4 pages including references. If NO: Cut more. No exceptions.
- [ ] **GO:** Paper 2 dataset stats match `wc -l` output. If NO: Fix numbers immediately.
- [ ] **GO:** HuggingFace URL appears in Paper 2. If NO: Add it.

### Risk Mitigation (Day 4)

| Risk | Mitigation |
|------|------------|
| References are messy / incomplete | Yanmife uses Google Scholar "BibTeX" export for each citation. Abraham reviews for completeness. |
| Paper 2 is just a data dump | Abraham ensures Paper 2 has a narrative: "Low-resource figurative language is underrepresented; this dataset enables..." |
| Paper 1 and Paper 2 overlap too much | Paper 1 = methodology + failures. Paper 2 = resource + application. If overlap >20%, rewrite. |

---

## Day 5 (Wednesday): Internal Review & Revision

### Morning: Cross-Review (All hands, 4 hours)

**Review Assignments:**
- **Abraham** reads Paper 2 for clarity, flow, and narrative coherence.
- **Yanmife** reads Paper 1 for technical accuracy — every number, every p-value, every confidence interval.
- **Iremide** reads BOTH papers for grammar, style, formatting, and figure quality.

**Review Format:** Each reviewer creates a Google Doc / Overleaf comment with:
1. Critical issues (must fix)
2. Suggestions (nice to fix)
3. Praise (what works)

### Afternoon: Revision (4 hours)

**Abraham**
- Address all critical issues on Paper 1.
- Polish the title. Options:
  - "When Adversarial Distractor Generation Fails: A Cross-Lingual Failure Taxonomy for Proverb Understanding"
  - "Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding"
- Finalize author order and affiliations.

**Yanmife**
- Address all critical issues on Paper 1 numbers and Paper 2 baselines.
- Run one final local encoder baseline to confirm a key number if any doubt remains.
- Ensure all Paper 1 figures have correct captions with statistical test names.

**Iremide**
- Address all grammar/style comments.
- Re-read the dataset card. Ensure it is NOT defensive but honest.
- Create `papers/eacl2027_findings/appendix.tex` with:
  - Full prompt templates
  - Complete model committee details
  - Extra statistical tables

### Evening (2 hours)

- Abraham compiles both papers. Checks page limits.
- All: 30-min final read of Paper 1. It should now be "submission-ready except for proofreading."

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| Paper 1 revision complete | Abraham | Overleaf |
| Paper 2 revision complete | Abraham | Overleaf |
| Appendix drafted | Iremide | `papers/eacl2027_findings/appendix.tex` |
| Review comment docs closed | All | Overleaf comments resolved |

### GO / NO-GO Checkpoint

- [ ] **GO:** Zero critical issues remaining in either paper. If NO: Fix tonight or cut the claim.
- [ ] **GO:** Paper 1 title clearly signals "methodology/failures," not "benchmark release." If NO: Rewrite title.
- [ ] **GO:** Dataset card does not claim human validation was done. If NO: Remove false claims.

### Risk Mitigation (Day 5)

| Risk | Mitigation |
|------|------------|
| Review reveals a fatal flaw | If Yanmife finds a wrong number: cut the sentence. If the flaw is structural (e.g., a core claim is unsupported), Abraham pivots the claim to what IS supported. |
| Ego battles over writing | Abraham has final say on Paper 1; Iremide has final say on dataset card; Yanmife has final say on numbers. Disputes resolved in 10-minute huddle. |

---

## Day 6 (Thursday): Submission Packaging & Final Proofreading

### Morning (4 hours)

**Abraham: Paper 1 Submission Package**
- Create ARR-compliant submission package:
  - `paper.pdf` (4 pages)
  - `appendix.pdf` (unlimited pages)
  - `references.bib`
- Write author response pre-draft (optional but recommended): a 1-page note anticipating reviewer objections and our responses.
- Check ARR submission portal for any last-minute format changes.

**Yanmife: Paper 2 arXiv Package**
- Create `arxiv_source.tar.gz` with:
  - `paper.tex`
  - `references.bib`
  - `figures/*.pdf`
  - `acl2024.sty` or equivalent style file
- Test compile locally: `pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`
- If compilation fails: fix immediately.

**Iremide: Final Dataset & Repository Cleanup**
- Update root `README.md` with:
  - Links to both papers (arXiv + ARR)
  - HuggingFace dataset link
  - Citation BibTeX
  - Team contact info
- Create GitHub release tag `v1.0-submission`.
- Ensure `DATA_PROVENANCE.md` and `ETHICS_STATEMENT.md` are in repo root.

### Afternoon (4 hours)

**All: Final Proofreading**
- Print Paper 1. Read aloud in rotation (each person reads one section, others listen).
- Print Paper 2. Read aloud in rotation.
- Fix any remaining typos, awkward phrasing, or formatting glitches.

**Abraham**
- Final check: Does Paper 1 cite Paper 2? (It should reference the dataset release.)
- Final check: Does Paper 2 cite Paper 1? (It should reference the methodology.)

**Yanmife**
- Final number check: Pick 5 random numbers from each paper. Verify against CSVs.
- Create `SUBMISSION_CHECKLIST.md` with all tasks done.

**Iremide**
- Final HuggingFace check: reload dataset, verify splits, check card renders correctly.
- Take screenshots of dataset card for records.

### Evening (2 hours)

- All: Relax. Light work only. Prepare for submission day.
- Abraham: Set alarm for submission day. Check ARR portal login credentials.

### End-of-Day Deliverables

| Deliverable | Owner | Location |
|-------------|-------|----------|
| ARR submission package ready | Abraham | `papers/eacl2027_findings/submission/` |
| arXiv source compiles cleanly | Yanmife | `papers/acl_dpi/arxiv_source.tar.gz` |
| GitHub release tagged | Iremide | Git tag `v1.0-submission` |
| `SUBMISSION_CHECKLIST.md` | Yanmife | `SUBMISSION_CHECKLIST.md` |
| Root `README.md` updated | Iremide | `README.md` |

### GO / NO-GO Checkpoint

- [ ] **GO:** arXiv source compiles on a FRESH machine (test in a temp directory). If NO: Fix LaTeX dependencies.
- [ ] **GO:** ARR PDF is ≤4 pages + appendix. If NO: Trim.
- [ ] **GO:** All team members have ARR portal login and ORCID. If NO: Create accounts tonight.

### Risk Mitigation (Day 6)

| Risk | Mitigation |
|------|------------|
| ARR portal downtime on deadline day | Submit on Day 7 morning, not evening. Avoid last-hour server load. |
| arXiv compilation fails | Yanmife tests compilation in a clean Docker container or fresh venv. |
| Forgotten password / ORCID issue | Test login on Day 6 evening. Reset passwords if needed. |

---

## Day 7 (Friday): SUBMISSION DAY

### Morning (4 hours): Final Polish

**9:00 AM — 15-min standup:**
- Each person states their one task for the morning.
- Abraham confirms submission timeline: Paper 1 to ARR by 2 PM; Paper 2 to arXiv by 5 PM.

**9:15 AM — 11:00 AM:**
- **Abraham:** Final read-through of Paper 1. Focus on: (a) first sentence, (b) abstract, (c) contribution statement, (d) limitations.
- **Yanmife:** Final read-through of Paper 2. Focus on: dataset stats, baseline numbers, HuggingFace URL.
- **Iremide:** Final HuggingFace card check. Ensure no broken Markdown.

**11:00 AM — 12:00 PM:**
- All: Fix any last typos. Freeze both papers. No more content changes.

### Afternoon: Submission (4 hours)

**12:00 PM — 2:00 PM: Paper 1 → EACL ARR**
- Abraham logs into ARR submission portal.
- Uploads `paper.pdf`, `appendix.pdf`, `references.bib`.
- Enters metadata: title, abstract, authors, keywords, tracks (Resources & Evaluation; Multilingualism).
- Clicks submit.
- **Saves confirmation email / screenshot.**

**2:00 PM — 3:00 PM: Break.**

**3:00 PM — 5:00 PM: Paper 2 → arXiv**
- Yanmife logs into arXiv.
- Uploads `arxiv_source.tar.gz`.
- Enters metadata: title, abstract, authors, ACM class, comments.
- Selects license (arXiv non-exclusive license recommended).
- Clicks submit.
- **Saves confirmation email / arXiv ID.**

**5:00 PM — 6:00 PM: Final Repository Updates**
- Iremide updates `README.md` with arXiv ID and ARR submission confirmation.
- Abraham pushes final commit: `git commit -m "v1.0: EACL ARR + arXiv submission"`
- Iremide verifies GitHub release tag points to correct commit.

### Evening: Done.

- Team celebration (virtual or in-person).
- No work tomorrow.

### End-of-Day Deliverables

| Deliverable | Owner | Evidence |
|-------------|-------|----------|
| Paper 1 submitted to ARR | Abraham | Screenshot of ARR confirmation |
| Paper 2 submitted to arXiv | Yanmife | arXiv submission ID |
| Repository finalized | Iremide | Git tag `v1.0-submission` |

### GO / NO-GO Checkpoint

- [ ] **GO:** ARR confirmation received. If NO: Check portal, contact support immediately.
- [ ] **GO:** arXiv source processed without errors. If NO: Fix and re-upload.
- [ ] **GO:** Team has backups of all submission files. If NO: Copy to cloud storage now.

---

## Post-Submission: ACL DPI (Within 2 Weeks)

Paper 2 is on arXiv immediately. ACL DPI submission follows:
- Abraham adapts Paper 2 to ACL DPI format (slightly different from arXiv).
- Iremide ensures dataset card meets ACL DPI checklist.
- Submit to ACL DPI portal. No hard deadline, but target within 2 weeks of arXiv release.

---

## Budget Allocation

| Item | Cost | When |
|------|------|------|
| Free-tier API usage (Groq, NVIDIA) | $0 | Already used for N=50 |
| Overleaf premium (if needed) | $0-$15 | Day 1 |
| arXiv submission | $0 | Day 7 |
| ARR submission | $0 | Day 7 |
| **Emergency fund (human validation)** | **$400-500** | **Reserved for rebuttal period** |
| Total spent this week | ~$0 | — |

**Why reserve $500:** If Paper 1 gets reviewed and reviewers demand human validation, we hire native speakers during the 2-week rebuttal period. This is our insurance policy.

---

## Communication Protocol

| Channel | Purpose | Check Frequency |
|---------|---------|-----------------|
| Daily 9 AM standup (15 min) | Blockers, scope, morale | Once/day |
| Overleaf comments | Paper-specific feedback | Real-time |
| Shared Google Doc | Running notes, decisions | As needed |
| WhatsApp/Signal | Urgent only | As needed |

**Rule:** If a task will take >2 hours and is not on this plan, it requires Abraham's approval.

---

## Appendix: Paper 1 Section Word Budget (4 Pages)

| Section | Words | Lines (≈) | Notes |
|---------|-------|-----------|-------|
| Title + Authors | — | 3 | — |
| Abstract | 150 | 10 | — |
| 1. Introduction | 200 | 14 | End with contribution statement |
| 2. Related Work | 200 | 14 | 3 sub-sections, 1 paragraph each |
| 3. Methodology | 300 | 20 | Move prompts to appendix |
| 4. Experimental Setup | 150 | 10 | Languages, models, tests |
| 5. Results | 150 | 10 | Primary + per-language only |
| 6. Negative Results | 400 | 27 | **The star section. Maximize.** |
| 7. Discussion | 100 | 7 | Cross-lingual boundary |
| 8. Limitations | 100 | 7 | Honest, brief |
| 9. Conclusion | 75 | 5 | — |
| References | — | 15 | ~25 citations |
| **Total** | **~1,825** | **~142** | **≈ 4 pages** |

**Tables/Figures budget:** 3 tables + 2 figures = ~1 page. Text = ~3 pages.

---

## Appendix: Paper 2 Section Structure (6-8 Pages, ACL DPI)

| Section | Content |
|---------|---------|
| Abstract | Dataset summary, languages, size, intended use |
| 1. Introduction | Motivation: low-resource figurative language gap |
| 2. Related Work | Existing proverb/figurative-language datasets |
| 3. Dataset Description | Languages, sources, statistics, structure |
| 4. Collection Methodology | How proverbs were gathered, cleaned, deduplicated |
| 5. Data Quality | Contamination filter, dedup, known issues |
| 6. Demonstrated Application | MCQ construction (S1/S2) + N=50 pilot results |
| 7. Baselines | Encoder results, API committee results |
| 8. Ethics & Limitations | Cultural property, no human validation yet, planned work |
| 9. Conclusion | Release statement, HuggingFace URL, citation |

---

## Appendix: Pre-Submission Checklist (Day 7 Morning)

### Paper 1 (ARR)
- [ ] PDF is exactly 4 pages (not 3.9, not 4.1)
- [ ] Appendix is separate PDF
- [ ] All authors have ARR accounts
- [ ] Abstract is ≤250 words (ARR limit)
- [ ] No anonymization issues (this is not a blind submission — ARR is single-blind)
- [ ] Track selected: Resources & Evaluation AND Multilingualism
- [ ] Keywords include: proverb, figurative language, distractor generation, low-resource, Arabic, Yoruba

### Paper 2 (arXiv)
- [ ] Source compiles with `pdflatex` + `bibtex`
- [ ] All figures included in tarball
- [ ] arXiv metadata correct
- [ ] License selected
- [ ] No line numbers (remove if present)

### Dataset (HuggingFace)
- [ ] Dataset loads with `load_dataset()`
- [ ] Card renders without Markdown errors
- [ ] License specified
- [ ] Citation block present

---

*Plan created: June 7, 2026*  
*Target: Submit Paper 1 to EACL ARR and Paper 2 to arXiv within 7 days.*
