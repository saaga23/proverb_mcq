#!/usr/bin/env python3
"""Generate a 2-page state-of-work DOCX for the Fatima fellowship quota request."""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
import os

DOCX_NAME = "ProverbGap_State_of_Work_2026-06-22.docx"

# Selected figures: informative, v68 / paper-first outputs only to keep file lean.
FIGURES = [
    (
        "paper_first_outputs_2026-06-22_10-42-02/fig1_per_language_consensus.png",
        "Figure 1. Consensus accuracy by language (v68, N=5). English is easiest; Arabic and Yoruba are near random, showing the distractors are hard."
    ),
    (
        "paper_first_outputs_2026-06-22_10-42-02/fig3_status_and_repairs.png",
        "Figure 2. Generation status and mean repairs per MCQ. 44% of items needed fallback repairs; NLI/leak filters are the main drivers."
    ),
    (
        "kaggle_run_logs/v68/openrouter_pilot1_test_output/fig4_generator_variant_heatmap.png",
        "Figure 3. Generator x variant accuracy heatmap (v68). Performance varies by model and prompting strategy."
    ),
    (
        "paper_first_outputs_2026-06-22_10-42-02/fig4_failure_modes.png",
        "Figure 4. Failure modes documented across v58-v68. Each is a reproducible pipeline weakness we treat as a contribution."
    ),
]

def set_compact_style(doc):
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10.5)
    paragraph_format = style.paragraph_format
    paragraph_format.space_after = Pt(3)
    paragraph_format.space_before = Pt(0)
    paragraph_format.line_spacing = 1.05


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.font.name = 'Calibri'
        run.font.bold = True
        if level == 1:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        else:
            run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(4)
    return p


def add_para(doc, text, bold=False, italic=False, size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    p.paragraph_format.space_after = Pt(3)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Inches(0.25)
    return p


def add_figure(doc, path, caption):
    if not os.path.exists(path):
        add_para(doc, f"[Missing figure: {path}]", italic=True, size=9)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=Inches(2.9))
    p.paragraph_format.space_after = Pt(1)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    crun = cap.add_run(caption)
    crun.font.name = 'Calibri'
    crun.font.size = Pt(8.5)
    crun.font.italic = True
    crun.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    cap.paragraph_format.space_after = Pt(4)


def add_cost_table(doc):
    add_para(doc, "Table 1. OpenRouter cost progression across recent runs.", italic=True, size=9)
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    headers = ['Version', 'Date', 'Proverbs', 'MCQs', 'Cost (USD)']
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.name = 'Calibri'
            run.font.size = Pt(9)
    rows = [
        ('v58', '2026-06-20', '3', '45', '$0.22'),
        ('v61', '2026-06-20', '3', '36', '$0.19'),
        ('v65', '2026-06-21', '3', '36', '$0.19'),
        ('v68', '2026-06-22', '15', '180', '$0.85'),
        ('v70 (partial)', '2026-06-22', '15', '83*', '$0.42*'),
    ]
    for r in rows:
        row_cells = table.add_row().cells
        for i, val in enumerate(r):
            row_cells[i].text = val
            for run in row_cells[i].paragraphs[0].runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9)
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = note.add_run('*v70 stopped when the API key hit its monthly budget.')
    run.font.name = 'Calibri'
    run.font.size = Pt(8.5)
    run.font.italic = True
    note.paragraph_format.space_after = Pt(4)


def main():
    doc = Document()
    set_compact_style(doc)

    # Margins
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.55)
    section.right_margin = Inches(0.55)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    trun = title.add_run('ProverbGap MCQ -- State of Work & OpenRouter Quota Request')
    trun.font.name = 'Calibri'
    trun.font.size = Pt(15)
    trun.font.bold = True
    trun.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    title.paragraph_format.space_after = Pt(1)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mrun = meta.add_run('Sunday Aspita Abraham | 2026 Fatima Fellow | 22 June 2026')
    mrun.font.name = 'Calibri'
    mrun.font.size = Pt(9.5)
    mrun.font.italic = True
    meta.paragraph_format.space_after = Pt(6)

    # 1. What we are building
    add_heading(doc, '1. What we are building')
    add_para(doc,
        "ProverbGap MCQ is a cross-lingual benchmark that tests whether language models truly understand "
        "proverbs in English, Arabic, and Yoruba, or whether they are just exploiting surface shortcuts. "
        "We generate multiple-choice questions where the model must pick the correct English meaning of a proverb "
        "from three tempting distractors. The twist is that the distractors are generated adversarially and then "
        "audited by a blind committee of other models that see only the four answer choices -- not the proverb itself.")

    # 2. Why it matters
    add_heading(doc, '2. Why it matters')
    add_para(doc,
        "Proverbs are a good stress-test for LLMs because their meaning is rarely literal and often culture-specific. "
        "A model can score well on standard reading comprehension and still fail a proverb. Existing benchmarks usually "
        "release MCQs without validating whether the wrong options are genuinely tempting. We are trying to fix that, "
        "especially for low-resource languages like Yoruba where good evaluation data is scarce. "
        "This work builds on my track record of building low-resource NLP benchmarks, including an accepted oral "
        "presentation at Data Science Africa 2026 and a published PMLR paper on domain adaptation for African agriculture.")

    # 3. What we used the API for
    add_heading(doc, '3. What we used the OpenRouter API for')
    add_bullet(doc, "Distractor generation: multiple generator models (Qwen, Gemma, Gemini) produce candidate wrong options.")
    add_bullet(doc, "Blind audit: a disjoint committee of models (Llama, Mistral, Gemma, DeepSeek) votes on which option is correct without seeing the proverb.")
    add_bullet(doc, "Gold-meaning curation: a small model rewrites literal/awkward glosses into natural English.")
    add_bullet(doc, "LLM fallback test: an experimental distractor generator that produces proverb-specific hard negatives on demand.")

    # 4. Progress so far
    add_heading(doc, '4. Progress so far')
    add_para(doc,
        "Our cleanest scaled run so far is v68 (N=5): 15 proverbs, 4 prompt variants, 3 generators, 180 MCQs, "
        "costing $0.85. Keys were perfectly balanced across A/B/C/D and there were zero exact duplicates. "
        "The blind committee was only 56.7% accurate overall -- only modestly above the 25% random baseline -- which means "
        "the distractors are genuinely tempting. Arabic and Yoruba consensus accuracy stayed near 50-53%, "
        "exactly the difficulty range we want for a hard benchmark.")
    add_cost_table(doc)

    # Insert first two figures side-by-side-ish (stacked because python-docx columns are hard)
    add_figure(doc, FIGURES[0][0], FIGURES[0][1])
    add_figure(doc, FIGURES[1][0], FIGURES[1][1])

    # 5. The bottleneck
    add_heading(doc, '5. The bottleneck we hit')
    add_para(doc,
        "The main problem is our corpus-based fallback sampler. When the NLI paraphrase or correct-meaning-leak "
        "filter rejects a model-generated distractor, the pipeline pulls a replacement from other proverbs' meanings. "
        "Those replacements are often plausible enough for auditors to agree on, but wrong. In v68, 44% of items "
        "needed fallback repairs and 28% became high-consensus-wrong (3 of 4 auditors agreed on the wrong answer).")
    add_para(doc,
        "We attempted v70 with the LLM-based fallback generator at the same N=5 scale (15 proverbs total), but the "
        "run stopped after 83 MCQs because the OpenRouter API key hit its monthly budget. Once the cap was reached, "
        "every further model call returned HTTP 403 'Budget limit exceeded', the generator pool exhausted its "
        "substitutes, and the run crashed with 'No active generators remaining'. Without more quota we cannot scale "
        "to N=15 per language or confirm whether the LLM fallback fixes the HCW problem.")

    add_figure(doc, FIGURES[2][0], FIGURES[2][1])
    add_figure(doc, FIGURES[3][0], FIGURES[3][1])

    # 6. What we need
    add_heading(doc, '6. What we need')
    add_para(doc,
        "We are requesting an increase in the OpenRouter monthly quota. Based on v68 costs, we estimate about "
        "$10-15 in additional API credit would let us complete v70 at N=15 per language (45 proverbs total, ~3x the "
        "v68 cost of $0.85 -> ~$2.60), run the LLM-fallback ablation at the same N=5 scale (~$2-3), and generate the "
        "60-item human-validation sample. This will give us a rigorous, audited dataset and a clear answer on whether "
        "the fallback bottleneck can be solved.")

    # 7. Next steps
    add_heading(doc, '7. Next steps if quota is increased')
    add_bullet(doc, "Finish v70 N=15 generation and audit (~2-3 Kaggle runs).")
    add_bullet(doc, "Run human validation: 60 MCQs, 20 per language, 2-3 native speakers per language.")
    add_bullet(doc, "Draft and submit a methodology paper to EACL 2027 ARR (deadline 3 August 2026).")
    add_bullet(doc, "Release the pipeline, audit logs, and dataset as a reproducible testbed.")

    doc.save(DOCX_NAME)
    print(f"Saved {DOCX_NAME}")


if __name__ == '__main__':
    main()
