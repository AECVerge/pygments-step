---
title: Entities
---

# Entities

In a Part 21 file an entity instance is `#n=` and every use of it later is
`#n`. `StepFileLexer` tokenises the two differently: the **definition** `#n=`
as `Name.Label`, and a **reference** `, #n ,` as `Name.Variable`, so the two
read differently in rendered output (see `test_step_instance_definition_vs_reference`).

```step21 title="definition vs. reference"
#1= CARTESIAN_POINT('',(0.,0.,0.));
#2= AXIS2_PLACEMENT_3D('',#1,#3,$);
#3= DIRECTION('',(0.,0.,1.));
#4= CARTESIAN_POINT('',#1,#2);
```

Entity (and typed-parameter) names are recognised structurally as `Name.Class`
when followed by `(` — so `CARTESIAN_POINT(`, `AXIS2_PLACEMENT_3D(` and
`DIRECTION(` all highlight as class names regardless of schema.

## User-defined keywords

A `!`-prefixed identifier is a user-defined keyword (ISO 10303-21 clause 5.3.1).
`!USER_DEFINED_KEYWORD(` is a class name; a bare `!USER_DEFINED_KEYWORD` is a
plain name.

```step21 title="user-defined keyword"
#10= EXTERNAL_REF(!USER_DEFINED_KEYWORD(1));
#11= EXTERNAL_REF(!USER_DEFINED_KEYWORD(2));
```

```step21 title="bare user-defined keyword"
!USER_DEFINED_KEYWORD
```
