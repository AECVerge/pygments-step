---
icon: material/home
title: Home
---

# pygments-step

[![PyPI version](https://img.shields.io/pypi/v/pygments-step.svg)](https://pypi.org/project/pygments-step/)
[![Python versions](https://img.shields.io/pypi/pyversions/pygments-step.svg)](https://pypi.org/project/pygments-step/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AECVerge/pygments-step/blob/main/LICENSE)

Pygments lexers for [EXPRESS](https://en.wikipedia.org/wiki/EXPRESS_(data_modeling_language)) (ISO 10303-11) and [STEP Part 21](https://en.wikipedia.org/wiki/ISO_10303-21) (ISO 10303-21).

[Repository](https://github.com/AECVerge/pygments-step){ .md-button }
[PyPI package](https://pypi.org/project/pygments-step/){ .md-button .md-button--primary }

## Install

```bash
pip install pygments-step
```

The only runtime dependency is `Pygments>=2.14`. Python 3.9+ is supported.

## What it does

Installing this package registers two lexers with Pygments, so every tool that
renders code through Pygments — MkDocs, Sphinx, `pygmentize`, Rich, Jupyter —
can highlight EXPRESS and STEP Part 21 without any further configuration.

| Lexer | Standard | Code fence | File types |
| --- | --- | --- | --- |
| `ExpressLexer` | EXPRESS, ISO 10303-11 | ` ```express ` | `*.exp` |
| `StepFileLexer` | Part 21 exchange file, ISO 10303-21 | ` ```step21 ` | `*.p21`, `*.stp`, `*.step` |

Both lexers are **schema-agnostic**: they lex the *languages*, not any single
application protocol, so they work equally well for IFC, AP203, AP214 or any
other STEP-based schema without carrying a schema-specific keyword table.

## Try it

See the [live demo](demo.md) for EXPRESS and STEP Part 21 snippets that are
highlighted by this exact package, the [quickstart](quickstart.md) for Python
and command-line usage, or [build from source](build.md) to produce and verify
the wheel yourself.

---

*MIT License © 2026 AECVerge*
