# Contributing to ProverbGap

Thank you for your interest in contributing to ProverbGap! Whether you're fixing a bug, improving documentation, adding a new language, or reporting a research finding, your help makes this project better for everyone.

This guide covers everything you need to know to contribute effectively.

---

## What Can I Contribute?

We welcome all kinds of contributions:

### Code and Engineering
- **Bug fixes** — Found something broken? Tell us in an issue or send a PR.
- **New features** — Better filters, improved prompts, additional generators, or pipeline optimizations.
- **Testing** — Add unit tests, integration tests, or Playwright E2E tests.
- **Infrastructure** — CI/CD improvements, Kaggle automation, deployment scripts.

### Documentation
- **Clarifications** — Fix typos, improve explanations, add examples.
- **Tutorials** — Walkthroughs for new contributors or researchers.
- **Translations** — Translate docs or the annotation interface into Arabic or Yoruba.

### Research and Data
- **Data corrections** — Fix proverb translations, meanings, or metadata. Open an issue tagged `data-correction`.
- **Analysis** — New metrics, visualizations, or statistical tests.
- **Validation** — Participate in human annotation or recruit other native speakers.

### Translations
We especially welcome **Arabic and Yoruba native speakers** who can:
- Review distractor quality for cultural appropriateness.
- Suggest improvements to gold-meaning curation.
- Translate the annotation interface and consent forms.

---

## Development Workflow

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/ProverbGap-MCQ.git
cd ProverbGap-MCQ
```

### 2. Create a branch

Use descriptive branch names:

```bash
git checkout -b fix/nli-filter-false-positive
git checkout -b feat/add-french-language-support
git checkout -b docs/improve-readme-quickstart
git checkout -b chore/update-openrouter-prices
```

**Branch naming convention:** `<type>/<short-description>`

| Type | When to use |
|------|-------------|
| `fix/` | Bug fixes |
| `feat/` | New features |
| `docs/` | Documentation only |
| `refactor/` | Code changes that neither fix bugs nor add features |
| `chore/` | Maintenance, dependencies, CI |
| `test/` | Adding or updating tests |

### 3. Make your changes

Follow the code style guidelines below. Run tests before committing.

### 4. Commit

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat(generation): add LLM-based fallback distractor generator"
```

**Commit message format:**

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, missing semicolons, etc. |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies, CI |

**Scopes:** `generation`, `evaluation`, `annotation_app`, `paper`, `docs`, `tests`, `ci`, `deps`

**Examples:**

```
feat(generation): add LLM-based fallback distractor generator
fix(evaluation): correct position bias in S2 assemble_mcq
docs(readme): update Quick Start with annotation app steps
chore(ci): add OpenRouter preflight smoke test
perf(pipeline): cache sentence-transformers embeddings
```

### 5. Push and open a PR

```bash
git push origin your-branch-name
```

Then open a Pull Request on GitHub. Fill in the PR template and link any related issues.

---

## Pull Request Checklist

Before opening a PR, confirm the following:

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New or modified functionality includes tests
- [ ] Python code passes `black` and `ruff`
- [ ] `annotation_app` passes `npm run lint` (if frontend changed)
- [ ] `AGENTS.md` is updated if the change affects agent handover
- [ ] `CHANGELOG.md` is updated under `[Unreleased]`
- [ ] Documentation is updated (README, paper sections, inline docs)
- [ ] No secrets or API keys are committed (verify `.gitignore`)
- [ ] Commit messages follow Conventional Commits

---

## Code Style

### Python

The Python pipeline uses **Black** for formatting and **Ruff** for linting.

```bash
# Format code
black src/ tests/ annotation_app/scripts/

# Lint code
ruff check src/ tests/ annotation_app/scripts/

# Type checking (if mypy is configured)
mypy src/
```

**Rules:**
- **Line length:** 88 characters (Black default).
- **Type hints:** Required for all new public functions and methods.
- **Docstrings:** Google style preferred.
- **Imports:** Sorted with `isort` (Black-compatible profile).

**Example:**

```python
from typing import Optional

def generate_distractor(
    proverb: str,
    meaning: str,
    language: str,
    temperature: float = 0.7,
) -> str:
    """Generate a single distractor for the given proverb.

    Args:
        proverb: The source proverb text.
        meaning: The curated English meaning.
        language: Source language code (`eng`, `ara`, `yor`).
        temperature: Sampling temperature for the LLM.

    Returns:
        A distractor string that passes all filter gates.
    """
    ...
```

### TypeScript / React (annotation_app)

The annotation app uses **ESLint** and **Prettier** (configured via `eslint.config.mjs`).

```bash
# Lint
npm run lint

# Format (if Prettier is set up as a separate script)
npx prettier --write src/
```

**Rules:**
- **Prefer functional components and hooks** over class components.
- **Keep components small and focused.** If a component exceeds ~150 lines, consider splitting it.
- **Use Tailwind CSS** for styling. Avoid inline styles or CSS modules unless absolutely necessary.
- **Type everything.** Use TypeScript types/interfaces for props and state.
- **No `any` types.** Use `unknown` or specific unions instead.

**Example:**

```tsx
interface AnnotationItem {
  id: string;
  proverb: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
}

function AnnotationCard({ item }: { item: AnnotationItem }) {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="rounded-lg border p-4">
      <p className="mb-4 text-lg font-medium">{item.proverb}</p>
      {/* options ... */}
    </div>
  );
}
```

---

## How to Run Tests

### Python tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_p0_filters.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Test files:**
- `test_p0_filters.py` — Validates blocklist, duplicate repair, leak sanitizer, and fallback sampler.
- `test_p1_nli.py` — Validates NLI paraphrase filter.
- `test_integration.py` — Lightweight mocked integration test of `generate_options`.
- `test_pilot1_nano_opus_local.py` — Full mocked end-to-end Pilot 1 TEST run (no API credits).

### Annotation app tests

```bash
# Run Playwright E2E tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run a specific test
npx playwright test e2e/annotation.spec.ts
```

### Pre-commit checks

Make sure everything passes before pushing:

```bash
# Python
black src/ tests/
ruff check src/ tests/

# Node
cd annotation_app
npm run lint
```

---

## How to Add a New Language

Adding a new language (e.g., French, Hausa, Swahili) to the pipeline requires changes in several places.

### 1. Add the language code and configuration

In the generation pipeline (typically `src/generation/pilot1_generator.py` or a config file), add:

```python
LANGUAGE_CONFIG = {
    "eng": {"name": "English", "script": "Latin", "nli_threshold": 0.58},
    "ara": {"name": "Arabic", "script": "Arabic", "nli_threshold": 0.45},
    "yor": {"name": "Yoruba", "script": "Latin", "nli_threshold": 0.45},
    "fra": {"name": "French", "script": "Latin", "nli_threshold": 0.55},  # NEW
}
```

### 2. Prepare the proverb corpus

- Add your cleaned proverb data to `data/cleaned/` (e.g., `data/cleaned/french_proverbs.csv`).
- Include columns for: `proverb`, `meaning`, `cultural_context`, `source`.
- Run any existing preprocessing scripts to normalize the data.

### 3. Update the data loader

Ensure the data loader can read the new corpus and produces `Proverb` objects with the correct language tag.

### 4. Update gold-meaning curation

If the new language produces literal or awkward English translations, add a `curate_<lang>_meaning()` function or extend the generic `curate_gold_meaning()` to handle it.

### 5. Update NLI and semantic filters

Add language-specific thresholds to `LEAK_THRESHOLD_BY_LANGUAGE` and `NLI_EMBEDDING_GUARD_BY_LANGUAGE` if the new language needs different sensitivity.

### 6. Update the blocklist

If the new language has common idioms that leak into distractors, add them to the idiom blocklist.

### 7. Update tests

Add test cases for the new language:

```python
def test_french_distractor_generation():
    proverb = load_proverb("fra", "FRA-001")
    mcq = generate_options(proverb, variant="adversarial-hard-negative")
    assert mcq.status != "parse_failure"
    assert mcq.distractors_are_plausible()
```

### 8. Update docs

- Add the language to `README.md` tables.
- Update `GETTING_STARTED.md` and `DATASET_CARD.md`.
- If deploying the annotation app, add the language to the UI locale options.

---

## Reporting Issues

### Bugs and feature requests

Open a GitHub issue with:
- A clear description of the problem or request.
- Steps to reproduce (for bugs).
- Expected vs. actual behavior.
- Relevant logs, screenshots, or CSV snippets.

### Data corrections

If you find errors in proverb translations or meanings:

1. Open an issue tagged `data-correction`.
2. Include the proverb ID, the current text, and the corrected text.
3. Cite your source if possible.

### Security vulnerabilities

**Do not open a public issue.** See [SECURITY.md](SECURITY.md) for private reporting instructions.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a welcoming and respectful environment.

- Be respectful and inclusive.
- Welcome newcomers and help them get started.
- Focus on constructive feedback.
- Respect differing viewpoints and experiences.

If you witness or experience unacceptable behavior, please report it to the project maintainers.

---

## Community

- **GitHub Issues:** Best for bugs, feature requests, and data corrections.
- **Discussions:** Use GitHub Discussions for questions, ideas, and general chat.
- **Email:** For private matters, contact the maintainers via the address in the repository profile.

Native speakers of **Arabic** and **Yoruba** are especially encouraged to contribute validation feedback on distractor quality and gold-meaning curation.

Thank you for helping make ProverbGap better!
