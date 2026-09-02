---
title: Literals
---

# Literals

## Strings

A Part 21 string is single-quoted; a doubled quote `''` inserts a quote into the
string (ISO 10303-21 clause 7.2).

```step21 title="strings"
#1= A('a simple string');
#2= A('it''s quoted');
#3= A('a string with a \X2\00E5\X0\ rune');
#4= A('');
```

## Binary literals

A double-quoted hex literal is a binary value (ISO 10303-21 clause 7.3):

```step21 title="binary literals"
#5= BINARY_HOLDER("0F3A");
#6= BINARY_HOLDER("00FF");
#7= BINARY_HOLDER("00000000");
```

In context:

```step21 title="literals in context"
#1= PROPERTY_SINGLE_VALUE('Name',$,STRING('value'));
#2= BINARY_HOLDER("0F3A");
#3= A('name','');
```

The `''` escape and the binary `"..."` hex form are handled by the same literal
rules as the fixture `sample.p21`.
