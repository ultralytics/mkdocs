# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, etc.) when working with code in this repository. CLAUDE.md is a symlink to this file.

`mkdocs-ultralytics-plugin` (AGPL-3.0) is the MkDocs plugin behind [docs.ultralytics.com](https://docs.ultralytics.com): it adds SEO metadata, social cards, JSON-LD structured data, git author and date footers, a "Copy for LLM" button, and `llms.txt` generation to built documentation.

## Core Principles (CRITICAL)

**Less is more. The simplest solution is the best solution.** The action hierarchy for every change: **Delete > Replace > Add**.

1. **Solve at the owner**: Put behavior in the code path that owns or observes it. For fixes, never guard a symptom with a staleness check, initialization flag, skip-first-call branch, or `try/except` around broken logic; relocate the trigger and delete the wrong path. For features, extend the existing owner rather than creating a parallel abstraction.
2. **Search and reuse first**: Search the whole repository before creating a feature, component, helper, workflow, or utility. Reuse or adapt what exists, consolidate in-scope duplication in the shared owner, and delete duplicate paths. Three similar lines beat a helper nobody else calls.
3. **Delete and modify existing code before creating new code**: Bugfixes are net-negative by default unless deletion and relocation are demonstrably impossible. A new file must first prove it cannot fit cleanly in an existing owner.
4. **Keep scope minimal**: Implement only the simplest complete solution. Avoid impossible-state handling, speculative flags, compatibility shims, policy scaffolding, and unrelated cleanup. Tests are out of scope by default — rely on existing coverage and focused validation; only an uncovered, high-risk regression path justifies minimal new test code.
5. **Ship zero-regression, production-ready changes**: Understand what you remove instead of retaining broken code as insurance. Remove unused imports, functions, types, files, and comments; run relevant cleanup checks; and thoroughly debug and validate the changed owner. Do not break existing features or workflows unless the PR intentionally removes them with evidence.

**Review gate:** for every addition, the reviewer decides whether deleting or changing existing code would have fixed the problem instead — if it would, that is a blocking finding. A missing or thin PR description is never itself a finding.

NEVER push to `main`. NEVER force push. Always start work in a new git worktree (`git worktree add`) on a feature branch and open a PR — never edit the primary checkout directly, it may hold in-flight work.

## PR Workflow

After opening a PR:

1. Wait for the automated PR review and auto-format commit from Ultralytics Actions (`format.yml`), then pull and address every finding.
2. Review the full diff in-session against the Core Principles, performance, and the review gate above, then batch the fixes into one commit and push. After each round of bot or human commits, pull and resume the same reviewer on `<last-reviewed-sha>..HEAD` plus anything that delta could have invalidated. Repeat until the local head matches the live head.
3. Hand off or merge only on a clean final pass: one cold full-diff review returning LGTM with no findings, on a head that is still live at merge time.
4. Never fight other commits: Ultralytics Actions pushes auto-format and header commits, and multiple users may work on the same PR. `git pull --rebase` before pushing; never reset or revert commits you did not author.
5. After the PR merges, clean up: remove local worktrees and branches for it, then `git checkout main && git pull`.

## Commands

```bash
# Install in editable mode with dev extras (pytest)
uv pip install -e ".[dev]"

# Lint and format, mirroring CI (.github/workflows/format.yml runs ultralytics/actions@main; there is no local ruff/lint config — that action is the source of truth for these flags)
uvx ruff check --fix --unsafe-fixes --extend-select F,I,D,UP,RUF,FA --target-version py38 --ignore BLE001,D100,D104,D203,D205,D212,D213,D401,D406,D407,D413,RUF001,RUF002,RUF012,S110 .
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
