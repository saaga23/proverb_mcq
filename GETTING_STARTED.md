# Getting Started with ProverbGap

> **No prior NLP or research experience required.** This guide explains the project in plain English, with a concrete example you can follow along.

---

## What is a "Proverb Gap"?

A **proverb** is a short, traditional saying that expresses a truth based on common sense or experience. Examples:

| Language | Proverb | Rough Meaning |
|----------|---------|---------------|
| English | "A bird in the hand is worth two in the bush" | Value what you have now over a risky future gain |
| Arabic | "اللي يطلب العالي يسقط الواطي" | He who reaches for the high falls to the low |
| Yoruba | "A kii yan eni ti o ni owo l'ori" | One does not choose the person with money on their head |

A **"gap"** in this context means a **missing piece** — specifically, we're testing whether AI can fill in the *correct meaning* of a proverb when given multiple choices. It's like a "fill-in-the-blank" quiz, but instead of a missing word, the missing piece is the *interpretation*.

The "ProverbGap" is also a research gap: existing AI benchmarks are too easy because the wrong answers (called **distractors**) are obviously bad. We build better, harder questions to stress-test AI comprehension.

---

## What are "Distractors"?

In a multiple-choice question (MCQ), a **distractor** is a wrong answer that looks plausible.

### A good distractor
- Feels like it *could* be correct to someone who doesn't fully understand the proverb.
- Is not obviously unrelated.
- Is close enough in meaning to the correct answer that you have to think carefully.

### A bad distractor
- Is obviously wrong ("A bird in the hand is worth two in the bush" → "Pizza is delicious").
- Is too long or too short compared to the correct answer.
- Repeats words from the proverb in a lazy way.

**Example MCQ:**

> **Proverb:** "A bird in the hand is worth two in the bush."
>
> **Which option best captures the meaning?**
> - **A.** Value what you have now rather than risking it for something better later.
> - **B.** Never go birdwatching without a camera.
> - **C.** Two birds are always better than one.
> - **D.** Hands are useful for catching animals.

Here, **A** is correct. **B** and **D** are bad distractors (obviously wrong). **C** is a *good* distractor — it's close to the right idea but reverses the logic. A smart test-taker has to actually understand the proverb to spot that **C** is wrong.

Our project's job is to generate more **C**-style distractors and fewer **B**/ **D**-style distractors.

---

## Why 3 Languages? Why These Specific Languages?

### Why multiple languages?

If we only tested English, we'd only measure how well AI understands English proverbs. By testing **three languages**, we can:
- Compare performance across high-resource (English) and low-resource (Yoruba) languages.
- See if AI "cheats" differently in different languages.
- Make sure our methods work beyond just English.

### Why English, Arabic, and Yoruba specifically?

| Language | Resource Level | Why it matters |
|----------|---------------|----------------|
| **English** | High | Most LLMs are trained on massive English text. This is our "easy" baseline. |
| **Arabic** | Medium | Written right-to-left, rich classical tradition (amsal), but underrepresented in LLM training data compared to English. |
| **Yoruba** | Low | A low-resource African language with tonal marks and deep oral tradition. LLMs often fail here because they have very little training data. |

**The goal is not to "trap" the AI.** The goal is to build an evaluation that is fair across languages and truly measures understanding, not memorization.

---

## The Full Pipeline (with a Real Example)

Here is what happens to a single proverb, step by step, using a real example.

### Step 1: Data

We start with a raw proverb from our corpus:

> **Proverb (English):** "A bird in the hand is worth two in the bush."
> **Raw meaning:** Better to value something certain than risk it for something better.

### Step 2: Gold-Meaning Curation

Sometimes the raw meaning is awkward or literal. A small LLM (`gpt-4.1-nano`) rewrites it into natural English:

> **Curated meaning:** "Value what you have now rather than risking it for something better later."

This curated meaning is what the model will try to match. It is **never** shown to annotators or auditors.

### Step 3: Generation

A **generator** LLM (e.g., `google/gemini-2.5-flash`) is asked to produce 3 distractors:

> **Prompt:** "Given the proverb '[X]' which means '[Y]', generate 3 plausible but incorrect meanings. Each must be a complete sentence, roughly the same length as the correct meaning, and must not be a generic English idiom."

The model returns something like:

- **A.** Value what you have now rather than risking it for something better later. *(correct)*
- **B.** Two birds are always better than one.
- **C.** Hands are useful for catching animals.
- **D.** Never go birdwatching without a camera.

### Step 4: Filtering (The Sanitizer Stack)

The raw distractors go through several filters:

| Filter | What it checks | Example rejection |
|--------|---------------|------------------|
| **Length parity** | All options should be roughly the same length | "A." is too short |
| **Blocklist** | Rejects generic English idioms | "The early bird catches the worm" |
| **Leak guard** | Rejects distractors that echo the correct meaning too closely | "Value what you have now..." |
| **Semantic distance** | Rejects distractors that are too similar to the correct meaning | Uses embeddings to measure similarity |
| **NLI filter** | Rejects paraphrases that a natural-language inference model considers "entailed" by the correct meaning | "Better to keep what you have..." |

If a distractor fails any filter, it is replaced by a **fallback sampler** — a curated pool of pre-written distractors from other proverbs.

After filtering:

- **A.** Value what you have now rather than risking it for something better later.
- **B.** Two birds are always better than one. *(passed)*
- **C.** Hands are useful for catching animals. *(passed)*
- **D.** Never go birdwatching without a camera. *(passed)*

### Step 5: Blind Audit

A separate **audit committee** of 4 LLMs votes on the correct answer. Crucially, they **do not see the proverb** — only the four options. This prevents them from using the proverb text as a shortcut.

| Auditor | Vote |
|---------|------|
| `llama-3.3-70b` | A |
| `mistral-small-3.2-24b` | A |
| `gemma-3-27b-it` | A |
| `deepseek-v3.2` | B |

**Consensus:** 3 out of 4 say A. The item passes the audit.

> If 3 or more auditors agree on a **wrong** answer, that's called a **HCW (High-Consensus-Wrong)** item. It's a red flag that our distractors are tempting but misleading.

### Step 6: Annotation

The hardest items (including HCW items) are sent to **human annotators** — native speakers who:
- Pick the correct answer.
- Rate how plausible each distractor is (1 = obviously wrong, 5 = could be correct).
- Flag shortcuts (e.g., "option D is twice as long as the others").

### Step 7: Analysis

Researchers compute:
- **Inter-annotator agreement (IAA):** Do humans agree with each other? (Measured by Fleiss' Kappa)
- **Consensus accuracy:** Do the LLM auditors agree with humans?
- **Shortcut resistance:** Are there fewer perfect-consensus items and fewer HCW items?

---

## Glossary of Terms

| Term | Definition | Example |
|------|-----------|---------|
| **Proverb** | A short, traditional saying expressing a truth or piece of advice. | "A stitch in time saves nine." |
| **Distractor** | A wrong answer in a multiple-choice question designed to look plausible. | "Two birds are always better than one." (wrong for the bird proverb) |
| **MCQ** | Multiple-Choice Question. A question with 4 options (A–D), one correct. | The bird proverb quiz above. |
| **LLM** | Large Language Model. The AI model generating or auditing questions. | GPT-4, Claude, Gemini, Llama. |
| **NLI** | Natural Language Inference. A task where a model decides if one sentence implies another. | Does "Value what you have" imply "A bird in the hand is worth two in the bush"? |
| **Semantic similarity** | A number (0–1) measuring how close two sentences are in meaning. | 0.9 = almost the same; 0.1 = totally different. |
| **Consensus** | Agreement among the audit committee. | 3 out of 4 auditors chose A → 75% consensus. |
| **Perfect consensus** | All auditors agree on the same answer. | 4 out of 4 chose A. |
| **HCW** | High-Consensus-Wrong. 3 or more auditors confidently pick the wrong answer. | 3 out of 4 chose B, but A was correct. |
| **Fallback sampler** | A backup pool of distractors used when LLM-generated ones fail filters. | A curated list of distractors from other proverbs. |
| **Gold meaning** | The curated, natural English meaning of a proverb used as the correct answer. | "Value what you have now rather than risking it for something better later." |
| **IAA** | Inter-Annotator Agreement. Do human annotators agree with each other? | Fleiss' Kappa = 0.65 (good agreement). |
| **Shortcut** | A superficial pattern that lets an AI (or human) answer correctly without true understanding. | "The longest answer is always right." |
| **Shortcut resistance** | How well a benchmark prevents AI from exploiting shortcuts. | A shortcut-resistant MCQ has no obvious patterns. |
| **Position bias** | The tendency for models to prefer certain answer positions (e.g., always pick C). | If auditors always pick B, that's position bias. |
| **Blind audit** | Auditors see only the options (A–D), not the source proverb. | Prevents the proverb text from giving away the answer. |
| **RPC** | Remote Procedure Call. A database function call (used by Supabase for concurrency). | `pg_get_items` fetches items atomically. |
| **RLS** | Row Level Security. A database feature restricting which rows a user can see. | Anonymous users can only insert annotations, not read others'. |
| **Concurrency lock** | A temporary lock preventing two annotators from working on the same item. | Lock expires after 30 minutes. |

---

## Next Steps

Now that you understand the basics, here's what to do next:

- **To run the pipeline locally:** Follow the setup in [README.md](README.md) under "I want to contribute code."
- **To annotate data:** Follow the setup in [annotation_app/README.md](annotation_app/README.md).
- **To read the research:** Check out [DATASET_CARD.md](DATASET_CARD.md) and [annotation/protocol.md](annotation/protocol.md).
- **To contribute code:** Read [CONTRIBUTING.md](CONTRIBUTING.md) for style guides and the PR process.

If anything is unclear, open an issue and ask. We're happy to help!
