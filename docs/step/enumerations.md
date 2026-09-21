---
title: Enumerations
---

# Enumerations

Indexed enumeration values are written between two dots, e.g. `.T.` and
`.UNSPECIFIED.`, and are emitted as `Name.Constant`. The unset value `$` and the
derived value `*` are emitted as `Keyword.Constant`.

```step21 title="enumeration values"
.T.
.F.
.UNSPECIFIED.
.NOTDEFINED.
```

The grammar of ISO 10303-21 allows only letters and digits between the dots, but
application protocol content uses underscores — IFC has values such as
`.LOADING_3D.` — so the lexer accepts them:

```step21 title="enumeration values with an underscore"
.LOADING_3D.
```

A strict validator would reject that value; the lexer colours it because that is
what the files contain.

```step21 title="unset and derived values"
$
*
```

In context:

```step21 title="enumerations in context"
#1= NAMED_UNIT(.T.,.F.,.UNSPECIFIED.);
#2= NAMED_UNIT(*,.F.,.UNKNOWN.);
#3= PROPERTY_SINGLE_VALUE('Ref',$,DIRECTION(0.,0.,1.),*);
#4= SI_UNIT(.MILLI.,.METRE.);
#5= BOOLEAN_VALUE(.T.);
```

Where a value is not known, `$` is used; where a value is derived from other
attributes, `*` is used.

```step21 title="a schema that uses unset and derived"
#1= CARTESIAN_POINT('',$,0.);
#2= AXIS2_PLACEMENT_3D('',#1,#3,$);
```
