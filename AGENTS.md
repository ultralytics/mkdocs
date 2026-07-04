# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, etc.) when working with code in this repository. CLAUDE.md is a symlink to this file.

## Core Principles (CRITICAL)

Respecting these principles is critical for every PR.

**Less is more. The simplest solution is the best solution.**

The action hierarchy for every change: **Delete > Replace > Add**. The best code change is a deletion. The second best is modifying what exists. Adding new code is the last resort.

1. **Minimal**: The simplest solution that works. Do not over-engineer, over-abstract, or add code just in case. Three similar lines beat a premature abstraction. Avoid error handling for impossible states, feature flags, compatibility shims, or policy scaffolding unless they are truly required.
2. **Solve at the source**: Do not hack fixes. Solve problems at their root. If something is broken, fix or remove the broken thing. Never patch over a broken abstraction, add workarounds, or add synchronization code for state that should not be duplicated.
3. **Delete ruthlessly**: When replacing code, delete what it replaced. Remove unused imports, functions, types, files, and commented-out code. Git preserves history. Run the repo's relevant dead-code or cleanup check when available.
4. **Replace > Add**: Modify existing code over adding new code. Edit existing files, extend existing components or functions with minimal parameters, and reuse existing utilities. If creating a new file, first prove it cannot fit cleanly in an existing file.
5. **Check existing**: Search the entire repo before creating anything new. If a feature, component, helper, responder, workflow, or utility already solves a similar problem, reuse or adapt it and delete the duplicate path.
6. **Deduplicate**: Do not duplicate existing code when updating the repo. Consolidate or refactor duplicates you find when it is in scope and low risk.
7. **Zero Regression**: Do not break existing features or workflows unless the PR intentionally removes them with evidence.
8. **Production ready**: All changes must be thoroughly debugged, validated, and production ready.

**When fixing bugs, ask: "What can I delete?" before "What can I replace?" before "What should I add?"**

## PR Workflow

After opening a PR:

1. Wait for the automated PR review and auto-format commit from Ultralytics Actions (`format.yml`), then pull and address every finding.
2. Launch an independent adversarial review agent with cold context (just the PR diff and this file) to hunt for bugs, regressions, and Core Principles violations — use the Codex CLI, one fresh `codex exec` run per round. Fix, push, and repeat until a fresh run reports LGTM.
3. Never fight other commits: Ultralytics Actions pushes auto-format and header commits, and multiple users may work on the same PR. `git pull --rebase` before pushing; never force-push, reset, or revert commits you did not author.
4. After the PR merges, clean up: remove local worktrees and branches for it, then `git checkout main && git pull`.

## Commands

```bash
# Install in editable mode with dev extras (pytest)
uv pip install -e ".[dev]"

# Lint and format, mirroring CI (.github/workflows/format.yml runs ultralytics/actions@main; there is no local ruff/lint config — that action is the source of truth for these flags)
uvx ruff check --fix --unsafe-fixes --extend-select F,I,D,UP,RUF,FA --target-version py39 --ignore D100,D104,D203,D205,D212,D213,D401,D406,D407,D413,RUF001,RUF002,RUF012 .
uvx ruff format --line-length 120 .
uvx --from ultralytics-actions ultralytics-actions-format-python-docstrings .

# Build sdist + wheel (as publish.yml does)
uv pip install build && python -m build
```

- There is no test suite and no test/coverage CI: `pytest` is declared in the `dev` extra of pyproject.toml, but the repo contains no tests.
- No CI version matrix; `requires-python >=3.8` is the floor declared in pyproject.toml, and package classifiers cover Python 3.8–3.14.

## Architecture

This repo is `mkdocs-ultralytics-plugin`, a PyPI package that enhances built documentation HTML with SEO meta tags (description/image/keywords), Open Graph and Twitter cards, JSON-LD structured data (Article + FAQPage), git date/author footers, social share buttons, a "Copy for LLM" button, and an `llms.txt` index. All source lives in the `plugin/` package:

- `plugin/processor.py` is the shared core: `process_html()` performs every HTML mutation, and `build_git_map()` collects per-file dates/author emails in a single `git log` pass.
- `plugin/main.py` defines `MetaPlugin` (registered as the `ultralytics` MkDocs plugin via the `mkdocs.plugins` entry point in pyproject.toml): `on_config` builds the git map once, `on_post_page` runs `process_html()` per page, `on_post_build` writes `llms.txt`.
- `plugin/postprocess.py` provides `postprocess_site()`, a standalone batch mode for any static site generator (Zensical, Hugo, Jekyll): it walks a built `site/` dir with a process or thread pool and calls the same `process_html()`; `generate_llms_txt()` lives here and is shared by both modes.
- `plugin/utils.py` resolves commit emails to GitHub usernames/avatars (noreply parsing → commits API → user search) with results cached in `mkdocs_github_authors.yaml`.

Publishing is gated in `.github/workflows/publish.yml`: it runs on every push to `main` (plus manual dispatch) but only for repo `ultralytics/mkdocs` and actor `glenn-jocher`, and only proceeds when `__version__` in `plugin/__init__.py` is a valid increment over the PyPI version (a patch bump of 1–2, a new minor ending in `.0`, or a new major ending in `.0.0`, per `should_publish()` in ultralytics-actions) — then it tags `v{version}`, creates a GitHub release, builds with `python -m build`, publishes via PyPI trusted publishing, uploads an SBOM, and notifies Slack.

## Conventions

- Every source file starts with the `# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license` header — Ultralytics Actions adds it automatically; don't add or revert it manually.
- Formatting is enforced by the Ultralytics Actions bot on PRs (`format.yml`): Ruff + docformatter for Python (120-char lines, Google-style docstrings with parenthesized types), Prettier for YAML/JSON/Markdown, codespell for spelling.
- Author resolution hits the live GitHub API and github.com at build time when `add_authors` or `add_json_ld` is enabled; results are cached in `mkdocs_github_authors.yaml` (written to `docs/` when it exists, else the cwd).
- Keep `requests>=2.28.1` unpinned upward — the pyproject.toml comment says not to raise it (conflicts with Ultralytics deps).
- Release process: bump `__version__` in `plugin/__init__.py` in a PR (patch bump of 1–2, or a new minor/major ending in zero); merging to `main` auto-publishes to PyPI via the gating above. No manual tagging.
