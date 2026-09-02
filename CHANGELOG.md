# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The `release` workflow now publishes automatically when a `v*` tag is pushed,
  targeting PyPI; the manual `workflow_dispatch` keeps the `testpypi` / `pypi`
  target choice.

### Changed

- Publishing to PyPI now uses OIDC Trusted Publishing
  (`pypa/gh-action-pypi-publish` with `id-token: write`), so the `PYPI_TOKEN`
  secret is no longer needed; TestPyPI still uses an API token.

## [0.1.0] - 2026-09-01

Initial release.

### Added

- `ExpressLexer` for the EXPRESS data modelling language (ISO 10303-11).
  Registered as `express`, with aliases `exp` and `iso-10303-11`, and bound to
  `*.exp` and the `text/x-express` MIME type.
  - Case-insensitive keywords, per ISO 10303-11 clause 7.
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
  `release.yml` (build + publish to TestPyPI, or to PyPI via a workflow input).

### Changed

- The source distribution (sdist) no longer carries `tests/` (or `docs/`,
  `.github/`, build artifacts). A `MANIFEST.in` now pins the sdist contents so
  test sources cannot leak in. The wheel is unaffected: it always contained only
  the `pygments_step` package.

### Notes

Both lexers are deliberately schema-agnostic: they lex the languages
themselves and carry no entity names from IFC or any other application
protocol. Consequently `ifc` and `*.ifc` are **not** claimed as an alias or
filename pattern — IFC is only one of many SPF-based formats. Use `step21`
(or `p21` / `spf`) for IFC content.

[Unreleased]: https://github.com/AECVerge/pygments-step/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AECVerge/pygments-step/releases/tag/v0.1.0
