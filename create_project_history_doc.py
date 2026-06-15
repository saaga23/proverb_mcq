"""
Create a plain-language Word document summarizing the ProverbGap MCQ project.
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path

OUT_PATH = Path("C:/Users/USER/Downloads/THe proverbeval container/MCQ/ProverbGap_MCQ_Project_History.docx")

doc = Document()

# Helper to add heading
def add_heading(text, level=1):
    return doc.add_heading(text, level=level)

# Helper to add normal paragraph
def add_para(text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    return p

# Helper to add bullet list
def add_bullet(text):
    doc.add_paragraph(text, style='List Bullet')

# Helper to add numbered list
def add_number(text):
    doc.add_paragraph(text, style='List Number')

# Title
title = doc.add_heading('ProverbGap MCQ: A Complete Project History', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_para("Plain-language summary for Sunday Aspita Abraham | June 2026").alignment = WD_ALIGN_PARAGRAPH.CENTER
add_para("This document explains the whole project journey-from the original idea to the current state-without technical jargon.").alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

# 1. What is ProverbGap?
add_heading("1. What is ProverbGap?", level=1)
add_para("ProverbGap is a research project that tests whether AI language models truly understand proverbs.")
add_para("A proverb is a short, wise saying like 'A friend in need is a friend indeed.' The words do not literally describe the meaning. To understand it, you need cultural and contextual knowledge. This makes proverbs a hard test for AI.")
add_para("The project focuses on three languages:")
add_bullet("English (high-resource: lots of digital text available)")
add_bullet("Arabic (medium-resource: complex grammar and script)")
add_bullet("Yoruba (low-resource: oral tradition, tonal language, less digital text)")
add_para("The goal is to build a benchmark-a standardized set of questions-that researchers can use to measure how well AI models understand figurative language across cultures.")

# 2. The Big Idea
add_heading("2. The Big Idea", level=1)
add_para("The project creates multiple-choice questions (MCQs) in two styles:")
add_number("Strategy 1 (S1) - the 'easy' baseline: The wrong answers are real meanings from other proverbs in the same language. If a model knows the language, it should still pick the correct meaning.")
add_number("Strategy 2 (S2) - the 'hard' adversarial test: A separate AI model rewrites the correct meaning in subtle ways to create wrong answers that sound very similar to the right one. This tests deeper understanding.")
add_para("Each proverb becomes one S1 question and one S2 question. Models are scored on both. If S2 is genuinely harder than S1, it shows the model cannot just rely on surface patterns.")

# 3. The Data Journey
add_heading("3. The Data Journey", level=1)
add_para("The team collected 7,172 proverbs across six languages. Here is the breakdown:")

# Table for data
table = doc.add_table(rows=7, cols=4)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Language'
hdr[1].text = 'Count'
hdr[2].text = 'Status in benchmark'
hdr[3].text = 'Notes'
rows = [
    ('English', '2,278', 'Used', 'Scraped from public proverb websites'),
    ('Arabic', '913', 'Used', 'Classical Arabic proverb collections'),
    ('Yoruba', '3,931', 'Used', 'From a published book of Yoruba proverbs'),
    ('French', '161', 'Collected only', 'Too small for reliable statistics'),
    ('German', '142', 'Collected only', 'Too small for reliable statistics'),
    ('Spanish', '63', 'Collected only', 'Too small for reliable statistics'),
]
for i, (lang, count, status, notes) in enumerate(rows, 1):
    r = table.rows[i].cells
    r[0].text = lang
    r[1].text = count
    r[2].text = status
    r[3].text = notes

add_para("")
add_para("Key data problems discovered along the way:")
add_bullet("Yoruba cleaning took much longer than expected. The source material had inconsistent spelling, missing tone marks, mixed dialects, and duplicates.")
add_bullet("English meanings sometimes contained the proverb text itself, creating a shortcut where models could simply reject the option containing the proverb.")
add_bullet("At least 2 of 50 Arabic items (4%) had wrong or misleading gold meanings.")
add_bullet("French, German, and Spanish samples were too small to include in the main benchmark.")
add_bullet("No human validation: native speakers have not yet reviewed the questions for quality.")
add_bullet("Data provenance documentation is incomplete, which reviewers flagged as a serious issue.")

# 4. Version History
add_heading("4. Version History: What Worked and What Broke", level=1)

add_heading("v1 - The Simple Beginning", level=2)
add_para("The first version was straightforward: build MCQs, run models, report accuracy. But it immediately revealed problems.")
add_bullet("Position bias: Models chose answer 'A' 85.6% of the time when it was correct, but only 64-67% for positions B, C, D. They were exploiting position, not reading.")
add_bullet("Same-family exploitation: A Meta model generated the distractors, and another Meta model evaluated them. The evaluator scored 57.8% on generated distractors versus 26.7% on human-written ones-not because it understood the proverbs, but because it recognized Meta's writing style.")
add_bullet("GPU models failed: ALLaM produced garbled text, AfroLLaMA showed suspicious memorization, and BLOOM ran out of memory. The team switched to API-only evaluation.")

add_heading("v2 - The API Meltdown", level=2)
add_para("The team tried to use multiple AI providers to make the system robust. Instead, it became fragile.")
add_bullet("DeepInfra returned payment errors and wrong model IDs.")
add_bullet("SambaNova timed out on every request.")
add_bullet("Cerebras had wrong model IDs.")
add_bullet("Groq rate-limited aggressively, causing 15,131 errors in one run.")
add_bullet("The committee shrank from 5 models to 3, then to 2.")
add_para("Lesson: API infrastructure is unreliable. The pipeline had to be redesigned to survive failures.")

add_heading("v3 - The S2 Crisis", level=2)
add_para("Strategy 2, the adversarial paraphrase approach, did not work well at first.")
add_bullet("Fallback rate exploded to 37.8%: the AI could not generate good wrong answers, so the system fell back to generic placeholders.")
add_bullet("Yoruba was worst affected, with 43.3% fallback.")
add_bullet("A kNN retrieval attempt generated nonsense like numbers ('20', '23', '30') as answer options.")
add_bullet("A multi-stage prompting method from the literature produced explanations instead of paraphrases, making questions trivially easy (100% accuracy).")
add_para("Fix: A dual-gate validation system was added. Generated options had to pass length and meaning checks. Retries were increased. Fallback rate dropped to 21.3%.")

add_heading("v4.3.3 - The Catastrophic Regression", level=2)
add_para("After a successful v4.3.2 run (85.4% S1, 69.3% S2), five 'minor' fixes were applied for v4.3.3. The result: S1 collapsed to 24.2% and S2 to 0.0%.")
add_para("Root cause: Not the code fixes, but an infrastructure cascade. NVIDIA timed out during health check and excluded one model. All worker threads then flooded the remaining Groq model, triggering rate limits. 769 of 790 evaluations failed.")
add_para("Recovery: Added health-check retries, provider cooldown waits, and dynamic worker caps. v4.3.4 restored performance: 86.8% S1, 62.5% S2.")

add_heading("v4.3.4 - The Hardened Pilot", level=2)
add_para("This version produced the main pilot results that appear in the paper draft.")

result_table = doc.add_table(rows=6, cols=3)
result_table.style = 'Light Grid Accent 1'
h = result_table.rows[0].cells
h[0].text = 'Metric'
h[1].text = 'Result'
h[2].text = 'What it means'
res_rows = [
    ('Strategy 1 accuracy', '86.8%', 'Easy baseline: models mostly get it right'),
    ('Strategy 2 strict accuracy', '62.5%', 'Hard adversarial questions'),
    ('S2 fallback rate', '21.3%', 'AI failed to generate good wrong answers'),
    ('McNemar test', 'p < 0.001', 'S2 is statistically harder than S1'),
    ('Per-language S2', 'English 71.3%, Arabic 65.5%, Yoruba 46.2%', 'Harder for lower-resource languages'),
]
for i, (m, r, mean) in enumerate(res_rows, 1):
    row = result_table.rows[i].cells
    row[0].text = m
    row[1].text = r
    row[2].text = mean

add_para("")
add_para("Important note: A later audit (June 4) raised a serious concern that the 62.5% S2 figure mixes real paraphrases (which scored only 24.9%, below random guessing) with fallback placeholder questions (which scored much higher). This means the headline 62.5% may not reflect genuine model understanding of hard distractors. The project team and reviewers disagree on how to interpret this.")

add_heading("June 2026 - Kaggle Reproducibility Push", level=2)
add_para("The team moved the pipeline to Kaggle so other researchers could reproduce the results.")
add_bullet("Initial Kaggle runs had catastrophic failure rates (~90%) due to invalid API keys and rate limiting on Kaggle's shared IP addresses.")
add_bullet("The team added 8 valid Groq keys, key validation, adaptive delays, and smart resumption.")
add_bullet("Latest run (June 9, 2026): 900/900 evaluations completed, failure rate dropped to 15.0%, zero HTTP 429 errors.")
add_bullet("However, a new S1 answer-key bug was discovered: S1 was generated twice in the same run, and the saved MCQ file no longer matches the evaluation results. S2 results are valid; S1 results from this run are not.")
add_bullet("The notebook has been patched and needs one more Kaggle run to produce fully trustworthy results.")

# 5. Hypotheses and Results
add_heading("5. Hypotheses Tested and What We Learned", level=1)

hyp_table = doc.add_table(rows=9, cols=3)
hyp_table.style = 'Light Grid Accent 1'
h = hyp_table.rows[0].cells
h[0].text = 'Hypothesis'
h[1].text = 'Result'
h[2].text = 'What we did about it'
h_rows = [
    ('S2 is harder than S1', 'Supported in pilot (86.8% vs 62.5%)', 'Reported as main result, but later audit questions whether the gap is real'),
    ('Models exploit answer position', 'Severe before fix (A-position 85.6%)', 'Added deterministic rotation and per-model shuffling'),
    ('Same-family generator + evaluator cheats', 'Confirmed (+31.1 pp inflation)', 'Switched S2 generator to qwen3-32b, different family from evaluators'),
    ('Chain-of-thought helps reasoning', 'Collapsed performance (~82% → ~48%)', 'Disabled CoT for models that failed under it'),
    ('kNN retrieval makes good distractors', 'Failed (generated numbers)', 'Abandoned'),
    ('Multi-stage prompting makes good distractors', 'Failed (100% accuracy, trivial)', 'Abandoned'),
    ('Encoder baselines perform poorly', 'Confirmed (~55% S1, ~30% S2)', 'Used as sanity check that task needs reasoning'),
    ('Famous English proverbs are memorized', 'Risk confirmed', 'Added contamination filter removing ~8.3% of English proverbs'),
]
for i, (hyp, res, action) in enumerate(h_rows, 1):
    row = hyp_table.rows[i].cells
    row[0].text = hyp
    row[1].text = res
    row[2].text = action

# 6. Reviewer and Mentor Concerns
add_heading("6. Reviewer and Mentor Concerns", level=1)
add_para("External reviewers and mentors raised many concerns. The most important are:")
add_number("S2 construct validity: Are the adversarial distractors genuinely hard, or are some unanswerable? The high fallback rate and the later audit's 24.9% real-paraphrase score suggest S2 needs careful scrutiny.")
add_number("Zero human validation: No native speakers have reviewed the questions. Top venues consider this a serious weakness.")
add_number("Data provenance: The sources of the proverbs are not fully documented, and permissions for the Yoruba book source are unclear.")
add_number("Hardcoded API keys: The code contains API keys in plain text, which is a security risk and prevents public sharing.")
add_number("Two-model committee: The final committee had only two reliable models. Reviewers prefer three to five models for robustness.")
add_number("Only one task: The benchmark only uses multiple-choice questions. Competitors like ProverbEval use MCQ + fill-in-the-blank + generation.")
add_number("Kaggle reproducibility: The notebook had improper cell markers, no version pinning, and no SIGTERM handler for Kaggle timeouts.")
add_number("Arabic gold-standard errors: At least 4% of Arabic items appear to have wrong meanings.")
add_number("Sample size: The pilot uses only 50 items per language. The planned scale is 700 per language.")

# 7. Current State
add_heading("7. Current State (June 13, 2026)", level=1)
add_para("The project is close to having a clean, reproducible Kaggle result, but one more run is needed.")
add_bullet("Infrastructure: SOLVED. Eight valid Groq keys eliminated rate-limit failures. Latest run failure rate is 15.0%, down from ~90%.")
add_bullet("Models: Current committee is Llama-3.3-70B, GPT-OSS-120B, and Qwen3-32B. GPT-OSS has a 45% empty-response rate, mostly for Arabic and Yoruba. Llama and Qwen are stable.")
add_bullet("S2 results from the latest Kaggle run are valid: 80.2% accuracy on saved MCQs.")
add_bullet("S1 results from the latest Kaggle run are corrupted by an answer-key shuffle bug. The notebook has been patched.")
add_bullet("The next concrete step is to delete old evaluation files and re-run the patched notebook on Kaggle once more.")

# 8. OpenRouter Credit Plan
add_heading("8. Plan for Using OpenRouter Credits", level=1)
add_para("OpenRouter provides access to many models through one API. Here is a focused plan for spending the credits wisely.")
add_heading("8.1 What OpenRouter can do for ProverbGap", level=2)
add_bullet("Diversify the evaluation committee. Currently the committee is small. OpenRouter can add reliable models like Claude, Gemini, or Mistral without managing separate provider accounts.")
add_bullet("Replace GPT-OSS-120B. GPT-OSS fails 45% of the time on non-English prompts. OpenRouter offers alternatives that may be more reliable for Arabic and Yoruba.")
add_bullet("Run S2 generation experiments. If qwen3-32b via Groq is ever rate-limited, OpenRouter can host the same or alternative generator models.")
add_bullet("Provide failover. If Groq or NVIDIA throttles Kaggle's shared IP, OpenRouter can keep the pipeline running.")

add_heading("8.2 Recommended model lineup to test", level=2)
models_table = doc.add_table(rows=5, cols=3)
models_table.style = 'Light Grid Accent 1'
h = models_table.rows[0].cells
h[0].text = 'Role'
h[1].text = 'Models to try'
h[2].text = 'Why'
m_rows = [
    ('Evaluator (general)', 'anthropic/claude-sonnet-4, google/gemini-1.5-pro', 'Reliable, strong multilingual performance'),
    ('Evaluator (Arabic)', 'anthropic/claude-sonnet-4, qwen/qwen3-32b', 'Good on Arabic figurative language'),
    ('Evaluator (Yoruba)', 'google/gemini-1.5-pro, anthropic/claude-sonnet-4', 'Better low-resource handling than GPT-OSS'),
    ('Generator (S2)', 'qwen/qwen3-32b, anthropic/claude-sonnet-4', 'Cross-family paraphrase generation'),
]
for i, (role, models, why) in enumerate(m_rows, 1):
    row = models_table.rows[i].cells
    row[0].text = role
    row[1].text = models
    row[2].text = why

add_heading("8.3 Budget priorities", level=2)
add_number("First, run a small N=10 or N=20 test through OpenRouter for each candidate model. Measure failure rate, cost per question, and accuracy. Do not run the full N=150 until you know the model works.")
add_number("Second, add one or two OpenRouter models to the main committee for the next Kaggle run. This gives you a 4-model committee instead of 3.")
add_number("Third, keep Groq as the primary provider because the 8-key rotation is now working. Use OpenRouter as failover and diversity, not as the main path.")
add_number("Finally, track costs per evaluation. OpenRouter pricing varies by model. Set a hard daily cap to avoid burning credits on failed retries.")

add_heading("8.4 What NOT to spend credits on", level=2)
add_bullet("Do not run large-scale S1/S2 generation experiments until the S1 answer-key bug is fully fixed and validated.")
add_bullet("Do not test exotic models with no proven multilingual track record.")
add_bullet("Do not use OpenRouter to replace the local encoder baselines-those run for free on CPU.")

# 9. Next Steps
add_heading("9. What to Do Next", level=1)
add_number("Re-run Kaggle once with the patched notebook. Delete eval_results.csv and eval_results_progress.csv first. Validate with audit_answer_key_consistency.py.")
add_number("Fix or clearly caveat S2 results. Decide whether to report the 62.5% headline figure, the stratified real-paraphrase vs fallback figures, or both.")
add_number("Fill in data provenance documentation. This is a publication blocker.")
add_number("Plan human validation. Even a small 100-item audit by native speakers would dramatically strengthen the paper.")
add_number("Decide the venue and scope. EACL 2027 ARR (deadline August 3, 2026) is the current target, but scaling to N=700 and adding tasks may not fit the timeline.")
add_number("Use OpenRouter credits for a small, controlled expansion of the evaluation committee, not for large-scale generation.")

# Footer
add_para("")
add_para("Document generated on June 15, 2026. All claims are based on project files, logs, and agent audits; contradictions between sources are noted where relevant.").alignment = WD_ALIGN_PARAGRAPH.CENTER

# Save
doc.save(OUT_PATH)
print(f"Saved: {OUT_PATH}")
