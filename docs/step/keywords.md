---
title: Keywords
---

# Keywords

The exchange-structure keywords of ISO 10303-21 are recognised as two families:
`ISO-10303-21` and `END-ISO-10303-21` are emitted as `Keyword.Namespace`, while
the section keywords are `Keyword.Reserved`. `HEADER`, `DATA` and `ENDSEC`
belong to the second edition; `ANCHOR`, `REFERENCE` and `SIGNATURE` open the
optional sections that the third edition (2016) added. They are case-insensitive,
like the EXPRESS lexer.

```step21 title="structure keywords"
ISO-10303-21
END-ISO-10303-21
HEADER
DATA
ENDSEC
ANCHOR
REFERENCE
SIGNATURE
```

A full minimal exchange file:

```step21 title="minimal Part 21 file"
ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(),(),'','','');
FILE_SCHEMA(('SOME_APPLICATION_PROTOCOL'));
ENDSEC;
DATA;
#1= THING(1);
ENDSEC;
END-ISO-10303-21;
```

`ANCHOR` and `REFERENCE` open optional sections of their own — they are not part
of the header section. Their items are written with tokens this lexer does not
claim yet, so the contents sit in a comment, which Part 21 allows wherever a
token separator may appear:

```step21 title="anchor and reference sections"
ANCHOR;
/* <part> = #20; */
ENDSEC;
REFERENCE;
/* #1 = <other.stp#2>; */
ENDSEC;
```

A signature section opens with the special token `SIGNATURE;` and closes with
`ENDSEC;` (clause 14.1). Its content is base64:

```step21 title="signature section"
SIGNATURE;
q1w2e3r4t5y6u7i8
ENDSEC;
```

Base64 that happens to use only letters and digits lexes as a name here; the
`+`, `/` and `=` characters it may also contain are not claimed yet.
