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
SIGNATURE;
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
of the header section. Their items are written with the third edition's
occurrence names and resources:

```step21 title="anchor and reference sections"
ANCHOR;
<part> = #20;
ENDSEC;
REFERENCE;
#1 = <other.stp#2>;
ENDSEC;
```

A signature section opens with the special token `SIGNATURE;` and closes with
`ENDSEC;` (clause 14.1). Its Base64 content is lexed line by line:

```step21 title="signature section"
SIGNATURE;
MIIG+/=
AA==
ENDSEC;
```

## Third-edition tokens

The productions the third edition adds render as follows:

```step21 title="resources, occurrence names, constant names and anchor tags"
#1= A(<other.stp#2>);
#2= B(@12,@PI,#PI);
ANCHOR;
<part> = #20 {tag_name:'anchor_item'};
ENDSEC;
```

* `<other.stp#2>` — a resource or an anchor name (`RESOURCE`, `ANCHOR_NAME`) is
  `String.Other`;
* `@12` — a value instance name is `Name.Label` where it defines the instance
  (`@12 = …`) and `Name.Variable` where it references one;
* `@PI` and `#PI` — a constant value name and a constant entity name are
  `Name.Constant`;
* `{tag_name:'anchor_item'}` — an anchor tag is `Name.Attribute`, and a string or
  a remark inside it may contain `}` without closing the tag early;
* the Base64 of the signature section above is `String.Other`, and may be written
  over several lines.
