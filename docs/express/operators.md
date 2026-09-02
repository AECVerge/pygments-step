---
title: Operators
---

# Operators

ISO 10303-11 keeps operator reserved words in a separate table (clause 7.2,
table 2) from the statement keywords, and `ExpressLexer` honours that split by
emitting `Operator.Word` for them. The symbolic operators are emitted as plain
`Operator`.

## Word operators (table 2)

```express title="word operators"
IF a AND b THEN
  a := a OR b;            -- OR
  a := a XOR b;           -- XOR
  a := a ANDOR b;         -- ANDOR
  a := a MOD b;           -- MOD
  a := a DIV b;           -- DIV
  IF a NOT IN b AND a LIKE b AND NOT c THEN
    a := TRUE;
  END_IF;
END_IF;
```

Each word operator on its own, so the family is easy to read at a glance:

```express title="word operators (one per line)"
AND
ANDOR
DIV
IN
LIKE
MOD
NOT
OR
XOR
```

## Symbolic operators

```express title="symbolic operators"
-- assignment and instance-comparison operators
a := b;                    -- :=
a :=: b;                   -- :=:  (instance equal, rel_op)
a :<>: b;                  -- :<>: (instance not equal, rel_op)

-- relational operators
p < q;                     -- <
p <= q;                    -- <=
p > q;                     -- >
p >= q;                    -- >=
p <> q;                    -- <>

-- arithmetic operators
r + s;                     -- +
r - s;                     -- -
r * s;                     -- *
r / s;                     -- /
r ** 2;                    -- **

-- remaining symbols recognised as operators
a || b;                    -- ||
@x, @y;                    -- @
\                           -- \
```

The `:=:` and `:<>:` forms are matched *before* the bare `:=`, so a relational
comparison is never split into an assignment operator and a stray colon (see
`test_express_instance_comparison_operators`).
