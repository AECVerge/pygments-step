---
title: Literals
---

# Literals

All literal forms that `ExpressLexer` can emit, with the token they produce.

## Strings

A simple string is single-quoted; a doubled quote `''` escapes a quote inside it
(clause 7.5.4):

```express title="strings"
s1 : STRING := 'hello';
s2 : STRING := 'it''s here';
s3 : STRING := 'a simple string';
```

## Encoded string literal

A double-quoted hex string is an encoded (hexadecimal) string literal. Each
character is encoded as four octets — the ISO/IEC 10646 group, plane, row and
cell — so the hexadecimal digits always come in groups of eight:

```express title="encoded string literal"
e1 : STRING := "000000E9";             -- one character
e2 : STRING := "00000041000000E9";     -- two characters
e3 : STRING := "1F2A3B";               -- not valid: a group is eight digits
```

The lexer colours `e3` as a string literal all the same: it renders the language
rather than validating it, and a partial group is still read as a hexadecimal
string. ISO 10303-11 clause 7.5.4, example 4, treats that literal as invalid,
so a validator should reject it.

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
