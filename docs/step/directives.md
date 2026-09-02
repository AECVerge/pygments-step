---
title: Directives
---

# Directives

Part 21 uses backslash sequences for control information inside strings
(ISO 10303-21 table 4) and for print control (table 6), the latter allowed
*wherever a token separator may appear* (clause 11) and therefore also inside
strings.

## String control directives (table 4)

These are only meaningful inside a string, which is where the lexer recognises
them as `String.Escape`:

```step21 title="string control directives"
#1= A('Nordm\X2\00F8\X0\ller');
#2= A('\X4\0001F600\X0\');
#3= A('a\S\c');
#4= A('\P\A\aged');
#5= A('\X\E9');
```

* `\X2\00F8\X0\` — a Unicode character (ISO 8859 / 10646 escape);
* `\X4\0001F600\X0\` — a full ISO 10646 escape;
* `\S\c` — a single character on the current page;
* `\P\A\` — a character from page A (one of the `\P?` forms);
* `\X\E9` — a two-digit hexadecimal escape.

## Print control directives (table 6)

`\N\` (new page) and `\F\` (start of new file) are recognised **inside** a string
as `String.Escape`:

```step21 title="print directives inside a string"
#1= A('one\N\two');
#2= B('first\F\second');
```

and **outside** a string as `Comment.Preproc`, where a token separator may
appear:

```step21 title="print directives outside a string"
#1= A(1);
\N\
#2= B(2);
\F\
```

The `\X2\..\X0\` and `\X4\..\X0\` forms must appear with an even number of hex
digits, and `\X\` takes exactly two, which the lexer enforces.
