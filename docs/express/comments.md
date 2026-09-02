---
title: Remarks
---

# Remarks

EXPRESS has two comment forms (ISO 10303-11 clause 7): the embedded remark
`(* ... *)` which **nests**, and the tail remark `-- ...` which runs to the end
of the line.

## Embedded remarks

```express title="embedded remarks"
(* a single-line remark *)

(* an embedded remark that
   (* nests *)
   and keeps going until the matching *) *)

SCHEMA probe;
  (* remarks can sit anywhere whitespace can *)
END_SCHEMA;
```

## Tail remarks

```express title="tail remarks"
SCHEMA probe;   -- this is a tail remark
ENTITY item;    -- it ends at the end of the line
END_ENTITY;     -- another one
END_SCHEMA;
```

## The two together

```express title="remarks in practice"
(* top-of-schema description *)
SCHEMA remark_probe;
  (* (* a remark (* inside (* a remark *) inside *) a remark *) *)
  CONSTANT
    c : REAL := 1.0;      -- tail remark after a constant
  END_CONSTANT;
END_SCHEMA;  -- tail remark closing the schema
```

The `(*` / `*)` delimiters can also appear literally inside a `--` tail remark
without opening a comment, because the tail remark runs to end of line first:

```express title="delimiters inside a tail remark"
-- a tail remark (* that is NOT a comment *) still runs to end of line
SCHEMA probe;  -- (* likewise stays a comment *)
END_SCHEMA;
```
