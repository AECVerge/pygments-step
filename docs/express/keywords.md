---
title: Keywords
---

# Keywords

Every reserved word of ISO 10303-11 (clause 7.2, table 1) is listed below and
is recognised by `ExpressLexer` as a keyword, type or declaration — **never** as
a plain identifier. The lexer is case-insensitive, so the upper-case form is the
canonical one used throughout the standard.

The `ExpressLexer` splits this table across three token families: the reserved
words in table 1 carry `Keyword` or (for the declaration heads, see
[Declarations](declarations.md)) `Keyword.Declaration`, while the aggregation and
built-in types are classified as `Keyword.Type` and are covered on the
[Types](types.md) page.

```express title="all reserved words"
ABSTRACT       AGGREGATE      ALIAS          ARRAY          AS
BAG            BASED_ON       BEGIN          BINARY         BOOLEAN
BY             CASE           CONSTANT       DERIVE         ELSE
END            END_ALIAS      END_CASE       END_CONSTANT   END_ENTITY
END_FUNCTION   END_IF         END_LOCAL      END_PROCEDURE  END_REPEAT
END_RULE       END_SCHEMA     END_SUBTYPE_CONSTRAINT       END_TYPE
ENTITY         ENUMERATION    ESCAPE         EXTENSIBLE     FIXED
FOR            FROM           FUNCTION       GENERIC        GENERIC_ENTITY
IF             INTEGER        INVERSE        LIST           LOCAL
LOGICAL        NUMBER         OF             ONEOF          OPTIONAL
OTHERWISE      PROCEDURE      QUERY          REAL           RENAMED
REFERENCE      REPEAT         RETURN         RULE           SCHEMA
SELECT         SET            SKIP           STRING         SUBTYPE
SUBTYPE_CONSTRAINT            SUPERTYPE      THEN           TO
TOTAL_OVER     TYPE           UNIQUE         UNTIL          USE
VAR            WHERE          WHILE          WITH
```

A single snippet that exercises many of them together, in the syntactic positions
where they are usually found:

```express title="keywords in context"
SCHEMA keyword_probe;                          -- SCHEMA

CONSTANT
  k_scale : REAL := 1.0;                       -- CONSTANT
END_CONSTANT;                                  -- END_CONSTANT

TYPE t_id = INTEGER;
END_TYPE;                                      -- END_TYPE

ENTITY probe_item
  ABSTRACT SUPERTYPE OF (ONEOF(probe_a, probe_b))
  SUBTYPE OF (thing);                          -- ABSTRACT SUPERTYPE ONEOF SUBTYPE OF
    name      : STRING;
    count     : INTEGER;
  DERIVE
    doubled   : INTEGER := count * 2;
  INVERSE
    used_in   : SET [0:?] OF item FOR owner;
  WHERE
    wr1       : count >= 0;
END_ENTITY;                                    -- END_ENTITY

FUNCTION plus_one(x : NUMBER) : NUMBER;
  LOCAL
    r : NUMBER := 1;
  END_LOCAL;                                   -- END_LOCAL
  RETURN (r + x);                              -- RETURN
END_FUNCTION;                                  -- END_FUNCTION

RULE positive FOR (probe_item);
  WHERE
    wr1 : SIZEOF(QUERY (p <* probe_item | p.count <= 0)) = 0;
END_RULE;                                      -- END_RULE

END_SCHEMA;                                    -- END_SCHEMA
```
