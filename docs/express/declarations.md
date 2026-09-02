---
title: Declarations
---

# Declarations

EXPRESS describes a schema as a set of declarations. `ExpressLexer` highlights
the *declaration head* keyword as `Keyword.Declaration` and, when the head is
followed by a declared name, that name as `Name.Class` — so the identifier you
are actually defining stands out from the keyword that introduces it.

```express title="declaration heads"
SCHEMA        geometry_primitives;        -- SCHEMA + declared schema name
  TYPE
    t_id      = INTEGER;                  -- TYPE + defined type name
  END_TYPE;

  ENTITY
    point     : SUBTYPE OF (thing);       -- ENTITY + defined entity name
    -- body omitted
  END_ENTITY;

  FUNCTION
    area      (p : point) : REAL;         -- FUNCTION + defined function name
    -- body omitted
  END_FUNCTION;

  PROCEDURE
    scale_it  (p : point);                -- PROCEDURE + defined procedure name
  END_PROCEDURE;

  RULE
    unique_p  FOR (point);                -- RULE + defined rule name
    -- body omitted
  END_RULE;

  CONSTANT
    k_zero    : REAL := 0.0;              -- CONSTANT + declared constant name
  END_CONSTANT;

  SUBTYPE_CONSTRAINT
    sc_world  FOR thing;                  -- SUBTYPE_CONSTRAINT + defined name
  END_SUBTYPE_CONSTRAINT;
END_SCHEMA;
```

## Declaration heads only

Each head is also recognised on its own, out of a declaration context:

```express title="declaration heads (bare)"
SCHEMA
ENTITY
TYPE
FUNCTION
PROCEDURE
RULE
CONSTANT
SUBTYPE_CONSTRAINT
```

Note that `TYPE` here is the declaration head, distinct from the built-in *type*
family on the [Types](types.md) page (`STRING`, `INTEGER`, `LIST`, …) — the
`ExpressLexer` keeps `Keyword.Declaration` apart from `Keyword.Type`.
