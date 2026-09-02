---
title: Constants
---

# Constants

ISO 10303-11 (clause 7.2, table 3) defines built-in constants; `ExpressLexer`
emits `Keyword.Constant` for all of them. The indeterminate value `?` is
included here rather than treated as an operator, and is matched *before* the
operator characters so it never becomes punctuation or an operator.

```express title="built-in constants"
?
SELF
CONST_E
PI
FALSE
TRUE
UNKNOWN
```

In context:

```express title="constants in context"
SCHEMA constant_probe;
  CONSTANT
    e     : REAL := CONST_E;        -- CONST_E
    pi_n  : REAL := PI;             -- PI
  END_CONSTANT;

  ENTITY point;
    ok    : BOOLEAN := TRUE;        -- TRUE
    bad   : BOOLEAN := FALSE;       -- FALSE
  WHERE
    wr1   : point <> UNKNOWN;       -- UNKNOWN
    wr2   : point = SELF;           -- SELF
  END_ENTITY;
END_SCHEMA;
```

`?` is the indeterminate constant used for an unknown value or an open bound:

```express title="the indeterminate constant"
x := ?;                 -- a value that is not known
SET [0:?] OF item;      -- an open upper bound
```

Note `CONST_E` here is the mathematical constant named in table 3, and must not
be read as the declaration head `CONSTANT` from the [Declarations](declarations.md)
page.
