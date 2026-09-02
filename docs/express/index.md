---
title: EXPRESS tests
---

# EXPRESS production tests

These pages are a rendered, exhaustive corpus for the `ExpressLexer`
(`pygments_step.express`). Every page is a *production test*: the snippets below
are highlighted and **must lex cleanly**. Two layers of automation hold them to
that promise:

1. **The docs build.** The site is built with `mkdocs build --strict` in the
   `docs` GitHub Actions workflow. A lexing or linking error turns the build
   red, so a broken snippet blocks the deploy.
2. **The pytest suite.** `tests/test_docs_pages.py` parses every `express`
   fence on these pages and asserts that the lexer produces **zero `Error`**
   tokens, and that each page really contains the whole family of tokens it
   claims to cover.

Use these pages the way you would use a checklist: pick an EXPRESS construct you
are changing, find its page, and confirm the highlighting matches what you
expect. If the lexer ever stops recognising something, the relevant page stops
being green.

## Pages

| Page | What it exercises |
| --- | --- |
| [Keywords](keywords.md) | Every reserved word (ISO 10303-11, clause 7.2, table 1) |
| [Operators](operators.md) | Word operators (table 2) and every symbolic operator |
| [Declarations](declarations.md) | Declaration heads and the declared name token |
| [Types](types.md) | Aggregation types and built-in types |
| [Constants](constants.md) | Built-in constants (table 3), incl. `?` and `SELF` |
| [Built-ins](builtins.md) | Built-in functions (table 4) and procedures (table 5) |
| [Literals](literals.md) | Strings, encoded and binary literals, reals and integers |
| [Remarks](comments.md) | Nested `(* ... *)` and `--` tail remarks |

The EXPRESS lexer is **case-insensitive** (ISO 10303-11, clause 7), so each page
shows the canonical upper-case form; every snippet is valid lower-case too.
