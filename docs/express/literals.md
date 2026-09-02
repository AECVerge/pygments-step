---
title: Literals
---

# Literals

All literal forms that `ExpressLexer` can emit, with the token they produce.

## Strings

A simple string is single-quoted; a doubled quote `''` escapes a quote inside it
(ISO 10303-11 clause 7):

```express title="strings"
s1 : STRING := 'hello';
s2 : STRING := 'it''s here';
s3 : STRING := 'a simple string';
```

## Encoded string literal

A double-quoted hex string is an encoded (hexadecimal) string literal:

```express title="encoded string literal"
e1 : STRING := "000000E9";
e2 : STRING := "1F2A3B";
```

## Binary literal

A `%` followed by binary digits:

```express title="binary literal"
b1 : BINARY := %10110;
b2 : BINARY := %0;
b3 : BINARY := %11111111;
```

## Numbers

```express title="integers and reals"
i1 : INTEGER := 42;
i2 : INTEGER := 0;
r1 : REAL := 3.14;
r2 : REAL := 1.5E-3;
r3 : REAL := 2.0E+10;
r4 : REAL := 1.;          -- trailing dot after the integer part
```

The `E`/`e` exponent, `+`/`-` signs and `%` prefix are all handled by the number
and binary rules.
