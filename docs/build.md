---
icon: material/package-variant-closed
title: Build from source
---

# Build from source

## Local build

Produce the wheel and sdist with `uv` (or `build`):

```bash
uv sync --extra test
uv build
```

For plain pip build tooling, the equivalent is `python -m build`. Both write to
`dist/`:

```text
dist/
  pygments_step-x.x.x-py3-none-any.whl
  pygments_step-x.x.x.tar.gz
```

Install a local wheel:

```bash
pip install dist/pygments_step-x.x.x-py3-none-any.whl
```

Verify the registration:

```py
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename

assert get_lexer_by_name("express").name == "EXPRESS"
assert get_lexer_by_name("step21").name == "STEP Part 21"
assert get_lexer_for_filename("schema.exp").name == "EXPRESS"
```

## Project layout

```text
pygments_step/
  __init__.py        # exported classes
  express.py         # ExpressLexer (ISO 10303-11)
  step21.py          # StepFileLexer (ISO 10303-21)
tests/
docs/                # this site
mkdocs.yml
pyproject.toml
```

## Development

Clone the repository and install with the `test` extra:

```bash
git clone https://github.com/AECVerge/pygments-step.git
cd pygments-step
```

Run tests:

```bash
uv sync --extra test   # or: pip install -e ".[test]"
uv run pytest          # or: pytest
```

Building the documentation site:

```bash
pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve           # live preview at http://localhost:8000
```

