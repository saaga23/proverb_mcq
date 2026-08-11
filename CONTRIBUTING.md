# Contributing

Thank you for your interest in contributing to ProverbGap. This document provides setup instructions and guidelines for developers and researchers.

## Developer Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 22.x and npm (for annotation app)
- Git
- OpenRouter API key (for running generation/evaluation locally)

### Python Environment

```bash
git clone https://github.com/<org>/ProverbGap-MCQ.git
cd ProverbGap-MCQ

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
```

All tests must pass before opening a pull request.

### Annotation App

```bash
cd annotation_app
cp .env.example .env.local
# Populate .env.local with your Supabase project URL and anon key
npm install
npm run lint
npm run dev
```

## Code Style

### Python

- Format with [Black](https://black.readthedocs.io/) (`black src/ tests/`)
- Lint with [Ruff](https://docs.astral.sh/ruff/) (`ruff check src/ tests/`)
- Type hints are required for all new public functions and methods
- Docstrings should follow Google style

### TypeScript / React (annotation_app)

- Lint with [ESLint](https://eslint.org/) (`npm run lint`)
- Format with [Prettier](https://prettier.io/) (configured via `eslint.config.mjs`)
- Prefer functional components and hooks
- Keep components small and focused

## Commit Conventions

This repository follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type       | Description                                  |
|------------|----------------------------------------------|
| `feat`     | New feature                                  |
| `fix`      | Bug fix                                      |
| `docs`     | Documentation only changes                   |
| `style`    | Formatting, missing semicolons, etc.         |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf`     | Performance improvement                      |
| `test`     | Adding or updating tests                     |
| `chore`    | Maintenance, dependencies, CI, etc.          |

### Examples

```
feat(generation): add LLM-based fallback distractor generator
fix(evaluation): correct position bias in S2 assemble_mcq
docs(readme): update Quick Start with annotation app steps
chore(ci): add OpenRouter preflight smoke test
```

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

## Reporting Issues

- **Bugs and feature requests:** Open a GitHub issue with a clear description, reproduction steps, and expected vs actual behavior.
- **Security vulnerabilities:** See [SECURITY.md](SECURITY.md) for private reporting instructions. Do not open public issues for security problems.
- **Data corrections:** If you find errors in proverb translations or meanings, open an issue tagged `data-correction`.

## Community

- Be respectful and inclusive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- Native speakers of Arabic and Yoruba are especially encouraged to contribute validation feedback on distractor quality and gold-meaning curation.
