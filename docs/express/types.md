---
title: Types
---

# Types

`ExpressLexer` classifies aggregation types and built-in types as `Keyword.Type`,
keeping them apart from the declaration head `TYPE` (see
[Declarations](declarations.md)).

```express title="built-in and aggregation types"
AGGREGATE
ARRAY
BAG
BINARY
BOOLEAN
ENUMERATION
EXTENSIBLE
GENERIC
GENERIC_ENTITY
INTEGER
LIST
LOGICAL
NUMBER
REAL
SELECT
SET
STRING
```

In a schema, the aggregation types appear as attribute domains, sometimes with a
width or bound:

```express title="types in context"
ENTITY types_probe;
  a0 : AGGREGATE OF thing;            -- AGGREGATE OF
  a1 : ARRAY [1:3] OF REAL;           -- ARRAY
  a2 : BAG [0:?] OF item;             -- BAG
  a3 : BINARY (32);                   -- BINARY (width_spec)
  a4 : BINARY (32) FIXED;             -- FIXED closes the width_spec
  a5 : BOOLEAN;                       -- BOOLEAN
  e0 : ENUMERATION OF (red, green, blue);   -- ENUMERATION OF
  g0 : GENERIC;                       -- GENERIC
  g1 : GENERIC_ENTITY;                -- GENERIC_ENTITY
  i0 : INTEGER;                       -- INTEGER
  l0 : LIST [1:2] OF STRING;          -- LIST OF STRING
  l1 : LIST OF UNIQUE item;           -- LIST OF UNIQUE
  n0 : LOGICAL;                       -- LOGICAL
  n1 : NUMBER;                        -- NUMBER
  r0 : REAL;                          -- REAL
  s0 : SELECT (a, b, c);              -- SELECT
  s1 : SET [0:?] OF item;             -- SET
  s2 : STRING (16);                   -- STRING
END_ENTITY;
```

`EXTENSIBLE` is used to mark `SELECT` and `ENUMERATION` types as open:

```express title="extensible"
TYPE colour = EXTENSIBLE ENUMERATION OF (red, green, blue);
END_TYPE;
TYPE anything = EXTENSIBLE GENERIC_ENTITY;
END_TYPE;
```
