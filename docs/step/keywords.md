---
title: Keywords
---

# Keywords

The exchange-structure keywords of ISO 10303-21 are recognised as two families:
`ISO-10303-21` and `END-ISO-10303-21` are emitted as `Keyword.Namespace`, while
the three section keywords and the anchor/reference/signature keywords are
`Keyword.Reserved`. They are case-insensitive, like the EXPRESS lexer.

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

`REFERENCE` and `SIGNATURE` belong to the exchange-structure header/context and
are reserved keywords, not entity names:

```step21 title="reference and signature"
REFERENCE;
SIGNATURE;
ENDSEC;
```
