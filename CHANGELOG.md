# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  - Built-in functions and built-in types.
- `StepFileLexer` for STEP Part 21 exchange files (ISO 10303-21).
  Registered as `step21`, with aliases `p21`, `step`, `stp` and `spf`, and bound
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
  - Binary literals (`"0F3A"`), user-defined keywords
    (`!USER_DEFINED_KEYWORD`) and `/* ... */` comments.
- Registration through `pygments.lexers` entry points, so installing the
  package is sufficient for MkDocs, Sphinx, `pygmentize` and any other
  Pygments-backed renderer to pick the lexers up. No configuration required.
- Test suite covering alias resolution, filename dispatch, and token-level
  regressions for both lexers, asserting that neither fixture produces an
  `Error` token. Runs under `pytest` or standalone via
  `python tests/test_lexers.py`.

### Notes

Both lexers are deliberately schema-agnostic: they lex the languages
themselves and carry no entity names from IFC or any other application
protocol. Consequently `ifc` and `*.ifc` are **not** claimed as an alias or
filename pattern — IFC is only one of many SPF-based formats. Use `step21`
(or `p21` / `spf`) for IFC content.

[Unreleased]: https://github.com/AECVerge/pygments-step/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AECVerge/pygments-step/releases/tag/v0.1.0
