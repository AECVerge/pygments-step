---
title: STEP tests
---

# STEP production tests

These pages are a rendered, exhaustive corpus for the `StepFileLexer`
(`pygments_step.step21`), the lexer for ISO 10303-21 (Part 21) exchange files.
Like the [EXPRESS tests](../express/index.md), every page is a *production
test*: the snippets are highlighted and **must lex cleanly**, and two layers of
automation keep them honest.

1. **The docs build.** The site is built with `mkdocs build --strict` in the
   `docs` GitHub Actions workflow, so a lexing or linking error blocks the
   deploy.
2. **The pytest suite.** `tests/test_docs_pages.py` parses every `step21`
   fence on these pages and asserts the lexer produces **zero `Error`** tokens,
   and that each page really contains the whole family of tokens it claims.

`StepFileLexer` is **schema-agnostic**: entity names are lexed structurally, so
these examples work for IFC, AP203, AP214 or any other Part 21 schema.

## Pages

| Page | What it exercises |
| --- | --- |
| [Keywords](keywords.md) | Exchange-structure keywords |
| [Entities](entities.md) | Instance definitions vs. references, user-defined keywords |
| [Enumerations](enumerations.md) | Indexed enumeration values, unset and derived values |
| [Literals](literals.md) | Binary literals and strings (including `''` escapes) |
| [Directives](directives.md) | String and print control directives |
| [Comments](comments.md) | `/* ... */` block comments |
