# pygments-step

[![PyPI version](https://img.shields.io/pypi/v/pygments-step.svg)](https://pypi.org/project/pygments-step/)
[![Python versions](https://img.shields.io/pypi/pyversions/pygments-step.svg)](https://pypi.org/project/pygments-step/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Pygments](https://pygments.org/) lexers for [EXPRESS](https://en.wikipedia.org/wiki/EXPRESS_(data_modeling_language)) (ISO 10303-11) and [STEP Part 21](https://en.wikipedia.org/wiki/ISO_10303-21) (ISO 10303-21).

| Lexer | Standard | Code fence | File types |
| --- | --- | --- | --- |
| `ExpressLexer` | EXPRESS, ISO 10303-11 | ` ```express ` | `*.exp` |
| `StepFileLexer` | Part 21 exchange file, ISO 10303-21 | ` ```step21 ` | `*.p21`, `*.stp`, `*.step` |

Additional aliases: `exp`, `iso-10303-11` for EXPRESS; `p21`, `step`, `stp`,
`spf`, `iso-10303-21` for Part 21.

Both lexers are **schema-agnostic**. They lex the *languages*, not any single
application protocol, so they work equally well for IFC, AP203, AP214 or any
other STEP-based schema without carrying a schema-specific keyword table.

## Install

```bash
pip install pygments-step
```

Or, with [uv](https://docs.astral.sh/uv/):

```bash
uv add pygments-step
```

The only runtime dependency is `Pygments>=2.14`. Python 3.9+ is supported.

Installing is all you need to do. The lexers register themselves with Pygments
through `pygments.lexers` entry points, so every tool that renders code through
Pygments — MkDocs, Sphinx, `pygmentize`, Rich, Jupyter — picks them up
automatically. There is no configuration step.

## Usage

### Markdown code fences

Tag a fence with `express` or `step21`:

````markdown
```express
ENTITY cartesian_point
  SUBTYPE OF (geometric_representation_item);
    coordinates : LIST [1:3] OF length_measure;
  DERIVE
    dim : INTEGER := HIINDEX(coordinates);
  WHERE
    valid_dim : SIZEOF(coordinates) <= 3;
END_ENTITY;
```
````

````markdown
```step21
ISO-10303-21;
HEADER;
FILE_SCHEMA(('SOME_APPLICATION_PROTOCOL'));
ENDSEC;
DATA;
#1= CARTESIAN_POINT('',(0.,0.,0.));
#4= AXIS2_PLACEMENT_3D('',#1,#3,$);
#6= NAMED_UNIT(.T.,.F.,.UNSPECIFIED.);
ENDSEC;
END-ISO-10303-21;
```
````

This works out of the box in MkDocs (including Material for MkDocs, whose
`pymdownx.highlight` extension delegates to Pygments) and in any other
Markdown pipeline backed by Pygments — no `mkdocs.yml` changes required.

### Python API

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

lexer = get_lexer_by_name("step21")
print(highlight("#1= CARTESIAN_POINT('',(0.,0.,0.));", lexer, HtmlFormatter()))
```

The classes can also be imported directly:

```python
from pygments_step import ExpressLexer, StepFileLexer
```

Dispatch by filename works as well:

```python
from pygments.lexers import get_lexer_for_filename

get_lexer_for_filename("schema.exp")   # EXPRESS
get_lexer_for_filename("model.stp")    # STEP Part 21
```

### Command line

```bash
pygmentize -l express schema.exp
pygmentize -l step21 -f html -O full,style=friendly -o model.html model.stp
```

Because the file extensions are registered, `-l` can usually be omitted:

```bash
pygmentize schema.exp
```

## What the lexers cover

### EXPRESS (ISO 10303-11)

- Case-insensitive keywords, per clause 7.
- Nested `(* ... (* ... *) ... *)` embedded remarks and `-- ...` tail remarks.
- Declaration heads (`SCHEMA`, `ENTITY`, `TYPE`, `FUNCTION`, `PROCEDURE`,
  `RULE`, `CONSTANT`, `SUBTYPE_CONSTRAINT`) highlight the declared name
  distinctly from the keyword.
- Literals: doubled-quote string escapes (`'it''s'`), binary literals
  (`%10110`), encoded string literals (`"000000E9"`), reals and integers.
- Built-in functions (`SIZEOF`, `HIINDEX`, `EXISTS`, `TYPEOF`, …) and built-in
  types (`INTEGER`, `LIST`, `SELECT`, `LOGICAL`, …).

### STEP Part 21 (ISO 10303-21)

- Exchange structure keywords: `ISO-10303-21`, `END-ISO-10303-21`, `HEADER`,
  `DATA`, `ENDSEC`, `ANCHOR`, `REFERENCE`, `SIGNATURE`.
- Entity instance **definitions** (`#1=`) are tokenised differently from
  **references** (`,#1,`), so the two read differently in rendered output.
- Enumerations (`.T.`, `.F.`, `.UNSPECIFIED.`), unset values (`$`) and derived
  values (`*`).
- String control directives: `\S\`, `\P?\`, `\X\`, `\X2\...\X0\`,
  `\X4\...\X0\`, plus `''` escapes.
- Print control directives `\N\` and `\F\`, both inside strings and at any
  position where a token separator may appear.
- Binary literals (`"0F3A"`), user-defined keywords (`!USER_DEFINED_KEYWORD`)
  and `/* ... */` comments.

### A note on IFC

IFC files are Part 21 files, so `StepFileLexer` handles them — but `ifc` and
`*.ifc` are **deliberately not claimed** as an alias or filename pattern. IFC
is only one of many SPF-based formats, and privileging it in a
standards-level lexer would be arbitrary. Use `step21` (or `p21` / `spf`) for
IFC content.

## Test

Clone the repository and install with the `test` extra:

```bash
git clone https://github.com/AECVerge/pygments-step.git
cd pygments-step
uv sync --extra test
uv run pytest
```

Or with pip:

```bash
pip install -e ".[test]"
pytest
```

The suite also runs standalone, without pytest:

```bash
python tests/test_lexers.py
```

Tests cover alias and filename registration, token-level regressions for both
lexers, and assert that neither fixture produces a single `Error` token.
Fixtures are small hand-written snippets committed to the repository on
purpose: the real buildingSMART `*.exp` schemas are fetched over the network
and gitignored, so they cannot serve as a reproducible corpus.

## License

[MIT](LICENSE)
