---
icon: material/rocket-launch
title: Quickstart
---

# Quickstart

## Install

```bash
pip install pygments-step
```

The lexers register themselves with Pygments through
`pygments.lexers` entry points. Installing the package is all you need — there
is no configuration step.

## Markdown code fences

Tag a fence with `express` or `step21`:

````markdown
```express
ENTITY cartesian_point
  SUBTYPE OF (geometric_representation_item);
    coordinates : LIST [1:3] OF length_measure;
  WHERE
    valid_dim : SIZEOF(coordinates) <= 3;
END_ENTITY;
```
````

This works out of the box in MkDocs (including Material for MkDocs, whose
`pymdownx.highlight` extension delegates to Pygments) and in any other Markdown
pipeline backed by Pygments.

## Python API

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

lexer = get_lexer_by_name("step21")
print(highlight("#1= CARTESIAN_POINT('',(0.,0.,0.));", lexer, HtmlFormatter()))
```

The classes can be imported directly:

```python
from pygments_step import ExpressLexer, StepFileLexer
```

And dispatch by filename works too:

```python
from pygments.lexers import get_lexer_for_filename

get_lexer_for_filename("schema.exp")   # EXPRESS
get_lexer_for_filename("model.stp")    # STEP Part 21
```

## Command line

```bash
pygmentize -l express schema.exp
pygmentize -l step21 -f html -O full,style=friendly -o model.html model.stp
```

Because the file extensions are registered, `-l` can usually be omitted:

```bash
pygmentize schema.exp
```


