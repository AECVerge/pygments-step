# Contributing to pygments-step

Everything you need to go from a clean checkout to a shipped release.

## What this is

`pygments-step` is a pair of [Pygments](https://pygments.org/) lexers:

- `ExpressLexer` — EXPRESS (ISO 10303-11), files `*.exp`
- `StepFileLexer` — STEP Part 21 exchange files (ISO 10303-21), `*.p21` / `*.stp` / `*.step`

Both are **schema-agnostic**: they lex the *languages*, not any single
application protocol, so they work for IFC, AP203, AP214 or any other STEP-based
schema without a schema-specific keyword table. Installing the package registers
them through `pygments.lexers` entry points — no configuration is needed.

## Quick start

Requires Python 3.9+ and [uv](https://docs.astral.sh/uv/) (or `pip`).

```bash
git clone https://github.com/AECVerge/pygments-step.git
cd pygments-step
uv sync --extra test            # or: pip install -e ".[test]"
uv run pytest                   # or: pytest
```

`nox` is a global tool (not a project dependency):

```bash
nox --version                   # confirm it is installed; install with `pip install nox`
```

## Project layout

```text
pygments_step/
  __init__.py        # exported classes + __version__
  express.py         # ExpressLexer (ISO 10303-11)
  step21.py          # StepFileLexer (ISO 10303-21)
tests/
  fixtures/          # sample.exp, sample.p21 (hand-written, committed on purpose)
  test_lexers.py     # token-level regression tests
  test_docs_pages.py # every code fence on the docs pages must lex with zero Errors
docs/
  express/, step/    # exhaustive "production test" pages for each lexer
  *.md               # quickstart, build, demo
noxfile.py           # nox sessions: bump, release
requirements-docs.txt
pyproject.toml
```

## Common commands

| Task | Command |
| --- | --- |
| Run the test suite | `uv run pytest` (or `python tests/test_lexers.py`) |
| Serve docs locally | `pip install -r requirements-docs.txt` then `mkdocs serve` |
| Build docs strictly | `mkdocs build --strict` |
| Build the package | `uv build` (or `python -m build`) |
| Bump the version | `nox -s bump -- 0.2.0` |
| Release (tag + publish) | `nox -s release -- 0.2.0` |

## Tests

The suite is the safety net for both the lexers **and** the docs:

- `tests/test_lexers.py` — alias resolution, filename dispatch, and token-level
  regressions; asserts neither fixture produces a single `Error` token.
- `tests/test_docs_pages.py` — parses every `express` / `step21` code fence on
  the `docs/express` and `docs/step` pages, asserts **zero `Error`** tokens, and
  checks that each page really covers the whole token family it claims.

When you change a lexer, **update the matching docs page too.** The two must stay
in sync; if they drift, the docs test goes red.

## Building the documentation

```bash
mkdocs build --strict
mkdocs serve           # live preview at http://localhost:8000
```

`mkdocs build --strict` turns any lexing or linking error into a failure, so the
docs build is itself a production test for the lexers.

## Releasing

Every release follows the same ending: **push a `vX.Y.Z` tag** pointing at a
commit on `main`. That tag is what triggers the `release` workflow.

### The short route (checkout `main` at the release commit)

```bash
# 1. bump the version, then review and add a CHANGELOG entry
nox -s bump -- 0.2.0
# 2. commit everything (GitHub Desktop is fine for commits)
git add -A && git commit -m "Bump to 0.2.0"        # or commit via Desktop
git push origin main
# 3. tag and push (this is the point of no return — it publishes to PyPI)
nox -s release -- 0.2.0
```

`nox -s release` guards against the usual mistakes before doing anything:

1. you are on `main`;
2. the working tree is clean;
3. the requested version matches `pyproject.toml`;
4. local `main` is not behind `origin/main`;
5. the tag does not already exist.

It then runs `git push origin main` → `git tag -a vX.Y.Z -m "..."` →
`git push origin vX.Y.Z`, which fires the `release` workflow (tests → publish to
PyPI via OIDC Trusted Publishing).

### If you develop on a branch and merge via PR

A PR **merge** only puts code on `main` (it triggers `ci` and `docs`, not
`release`). There is no "tag" step on merge. After the merge:

```bash
git checkout main
git pull                     # bring the merge commit into local main
nox -s release -- 0.2.0      # tags the merge commit and publishes
```

### GitHub Desktop gotcha

**GitHub Desktop does not push tags.** It only pushes commits. So even if the
tag shows in your local history, the release will not run until you push it from
a terminal:

```bash
git push origin v0.2.0
```

## What the CI/CD workflows do

| Workflow | Trigger | What it runs |
| --- | --- | --- |
| `ci.yml` | push to `main`, pull requests | tests on Python 3.9–3.13, then a strict docs build |
| `docs.yml` | push to `main` | `mkdocs build --strict` + deploy to GitHub Pages |
| `release.yml` | push a `v*` tag (or manual) | tests, then build + publish to PyPI via OIDC |

The docs site is published from the `gh-pages` branch root (GitHub Pages source
must be *Deploy from a branch → `gh-pages` → `/ (root)`*).

## Conventions & gotchas

- **Keep a changelog.** Add a `## [version] - date` section for every release,
  using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
- **Semantic versioning.** The git tag and `pyproject.toml` version must match.
- **Do not claim application protocols.** `ifc` and `*.ifc` are deliberately
  not an alias or filename pattern; use `step21` / `p21` / `spf` for IFC.
- **Case-insensitivity.** Both lexers use `re.IGNORECASE`; the docs show the
  canonical upper-case forms.
- **Publish target.** `release.yml` publishes to PyPI on a `v*` tag. To test on
  TestPyPI first, run the workflow manually from the Actions tab and choose
  `testpypi`.
