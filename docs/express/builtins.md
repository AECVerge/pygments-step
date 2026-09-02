---
title: Built-ins
---

# Built-ins

ISO 10303-11 tables 4 and 5 list built-in functions and procedures.
`ExpressLexer` recognises them as `Name.Builtin` **only in call position** (a
`(` may follow), which is what the `(?=\s*\()` lookahead enforces. Each call
below must therefore highlight the routine name as a built-in.

## Built-in functions (table 4)

```express title="built-in functions"
ABS(x)
ACOS(x)
ASIN(x)
ATAN(x)
BLENGTH(b)
COS(x)
EXISTS(x)
EXP(x)
FORMAT(x, y)
HIBOUND(x)
HIINDEX(x)
LENGTH(x)
LOBOUND(x)
LOG(x)
LOG2(x)
LOG10(x)
LOINDEX(x)
NVL(x, y)
ODD(x)
ROLESOF(x)
SIN(x)
SIZEOF(x)
SQRT(x)
TAN(x)
TYPEOF(x)
USEDIN(x)
VALUE(x)
VALUE_IN(x, y)
VALUE_UNIQUE(x)
```

## Built-in procedures (table 5)

```express title="built-in procedures"
INSERT(list, i, x);
REMOVE(list, i);
```

A schema that puts several of them to work:

```express title="built-ins in context"
ENTITY builtin_probe;
  WHERE
    wr1 : SIZEOF(USEDIN(SELF, 'POINT')) > 0;
    wr2 : EXISTS(SELF) AND TYPEOF(SELF) <> UNKNOWN;
    wr3 : HIBOUND(coords) - LOBOUND(coords) = LENGTH(coords) - 1;
END_ENTITY;
```

`SIZEOF` on its own — without the call parenthesis — is a plain identifier, not a
built-in:

```express title="not a built-in without the call"
SIZEOF            -- Name, not Name.Builtin
SIZEOF (x)        -- Name.Builtin followed by Whitespace then (
```
