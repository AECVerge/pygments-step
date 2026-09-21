# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-21

### Added

- Examples on the STEP pages for the sections the third edition adds (`ANCHOR`,
  `REFERENCE`, `SIGNATURE`) and for an enumeration value that contains an
  underscore.

### Fixed

- `ExpressLexer`:
  - Whitespace is the set in clause 7.1.5 — space, tab, line feed and carriage
    return — instead of `\s`, which also accepted form feed and vertical tab. The
    same set now drives the separator in the declaration rule and in the built-in
    call lookahead, so a character is no longer whitespace in one place and an
    error in another.
  - A declaration head no longer swallows the next reserved word as the declared
    name: `ENTITY ENUMERATION` lexes as a declaration head followed by the
    `ENUMERATION` type keyword, and the stacked heads on the declarations page
    stay declaration heads.
  - The declared name and every other identifier begin with a letter (clause
    7.4), so `_x` is an error rather than a name.
  - An unterminated string literal ends at the line end instead of turning the
    rest of the file into string text (clause 7.5.4: a string literal never spans
    a physical line boundary).
  - The symbolic operators are spelled out as explicit alternatives, longest
    first. `@` is no longer one of them: it is a special character of the
    character set (clause 7.1.3) but not a symbol of clause 7.3 table 6, and no
    operator uses it, so outside a string it is an error.
  - `_KEYWORDS` no longer repeats `CONSTANT`, which `_DECL` already carries, so
    the three tuples partition table 1 exactly (8 + 52 + 17 = 77).
- `StepFileLexer`:
  - Separation follows clause 5.6 — space plus the control characters the
    standards let an exchange structure ignore (line feed, carriage return, tab,
    vertical tab, form feed) — instead of `\s`; NUL, ESC and DEL stay errors. The
    same set drives the instance-definition and entity-name lookaheads.
  - A doubled reverse solidus is one `String.Escape` instead of two string
    characters (table 2 lists `REVERSE_SOLIDUS REVERSE_SOLIDUS` inside the
    `STRING` production).
  - `\X2\` and `\X4\` need at least one group of four or eight hexadecimal digits
    (table 4: `HEX_TWO { HEX_TWO }`), so an empty `\X2\\X0\` is no longer a
    complete escape.
  - A binary literal starts with the fill count, which is `0` to `3` (table 2),
    so `""` and values whose first digit is `4` to `F` are no longer binary
    literals; the empty binary is `"0"`.
- Both lexers keep to the ASCII lexical space their standards define, through
  `re.ASCII`. Without it a case-insensitive `[a-z]` matched KELVIN SIGN
  (U+212A) and long s (U+017F), and `\d` matched Arabic-Indic digits, so
  identifiers and numbers accepted text that is not in the standards' alphabets.
  Non-ASCII inside a string or a remark is unaffected.

### Notes

- The lexers stay permissive where the standards' own prose is a summary rather
  than the grammar: an encoded string literal whose hexadecimal digits do not
  come in whole characters is coloured as one string, and an enumeration value
  may contain an underscore — the WSN subsets of table 1 fold the underscore into
  `UPPER`, so that is ordinary grammar rather than a tolerance. Both are
  documented on the matching pages.
- Clause and table numbers in the code comments and on the pages cite the edition
  they come from: ISO 10303-11:2004 for EXPRESS and ISO 10303-21:2002 for STEP,
  with the third edition's renumbering noted on the STEP index page.
- The suite pins the rules above: the separator sets, declaration heads,
  identifiers, enumeration values, the string escapes and the binary fill count.

## [0.1.0] - 2026-09-02

Initial release.

### Added

- `ExpressLexer` for the EXPRESS data modelling language (ISO 10303-11).
  Registered as `express`, with aliases `exp` and `iso-10303-11`, and bound to
  `*.exp` and the `text/x-express` MIME type.
  - Case-insensitive keywords, per ISO 10303-11 clause 6.1 and annex A.1.1.
  - Nested `(* ... (* ... *) ... *)` embedded remarks and `-- ...` tail remarks.
  - Declaration heads (`SCHEMA`, `ENTITY`, `TYPE`, `FUNCTION`, `PROCEDURE`,
    `RULE`, `CONSTANT`, `SUBTYPE_CONSTRAINT`) tokenise the declared name
    separately from the keyword.
  - Doubled-quote string escapes (`'it''s'`), binary literals (`%10110`),
    encoded string literals (`"000000E9"`), reals and integers.
  - Built-in constants (`SELF`, `?`, `CONST_E`, `PI`, `TRUE`, `FALSE`,
    `UNKNOWN`), built-in functions and built-in types.
- `StepFileLexer` for STEP Part 21 exchange files (ISO 10303-21).
  Registered as `step21`, with aliases `p21`, `step`, `stp`, `spf` and
  `iso-10303-21`, and bound
  to `*.p21`, `*.stp`, `*.step` and the `application/x-step` and `model/step`
  MIME types.
  - Exchange structure keywords: `ISO-10303-21`, `END-ISO-10303-21`, `HEADER`,
    `DATA`, `ENDSEC`, `ANCHOR`, `REFERENCE`, `SIGNATURE`.
  - Entity instance definitions (`#1=`) tokenised distinctly from references
    (`,#1,`).
  - Enumerations (`.T.`, `.F.`, `.UNSPECIFIED.`), unset (`$`) and derived (`*`)
    values.
  - String control directives `\S\`, `\P?\`, `\X\`, `\X2\...\X0\` and
    `\X4\...\X0\`, plus `''` escapes.
  - Print control directives `\N\` and `\F\`, recognised both inside strings
    and wherever a token separator may appear.
  - Binary literals (`"0F3A"`), user-defined keywords
    (`!USER_DEFINED_KEYWORD`) and `/* ... */` comments.
- Registration through `pygments.lexers` entry points, so installing the
  package is sufficient for MkDocs, Sphinx, `pygmentize` and any other
  Pygments-backed renderer to pick the lexers up. No configuration required.
- Test suite covering alias resolution, filename dispatch, and token-level
  regressions for both lexers, asserting that neither fixture produces an
  `Error` token. Runs under `pytest` or standalone via
  `python tests/test_lexers.py`.
- Rendered production-test pages for both lexers under `docs/express` and
  `docs/step` (keywords, operators, types, declarations, constants, built-ins,
  literals, remarks / entities, enumerations, directives, comments), plus
  `tests/test_docs_pages.py`, which asserts every code fence on the pages lexes
  with zero `Error` tokens and that each page really covers its token family.
- GitHub Actions workflows: `ci.yml` (tests + strict docs build) and
  `release.yml` (build + publish to TestPyPI or PyPI). The `release` workflow
  publishes automatically when a `v*` tag is pushed, targeting PyPI, while the
  manual `workflow_dispatch` keeps the `testpypi` / `pypi` target choice.

### Changed

- The source distribution (sdist) no longer carries `tests/` (or `docs/`,
  `.github/`, build artifacts). A `MANIFEST.in` now pins the sdist contents so
  test sources cannot leak in. The wheel is unaffected: it always contained only
  the `pygments_step` package.
- Publishing to PyPI now uses OIDC Trusted Publishing
  (`pypa/gh-action-pypi-publish` with `id-token: write`), so the `PYPI_TOKEN`
  secret is no longer needed; TestPyPI still uses an API token.

### Notes

Both lexers are deliberately schema-agnostic: they lex the languages
themselves and carry no entity names from IFC or any other application
protocol. Consequently `ifc` and `*.ifc` are **not** claimed as an alias or
filename pattern — IFC is only one of many SPF-based formats. Use `step21`
(or `p21` / `spf`) for IFC content.

[0.2.0]: https://github.com/AECVerge/pygments-step/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AECVerge/pygments-step/releases/tag/v0.1.0
