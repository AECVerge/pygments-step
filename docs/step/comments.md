---
title: Comments
---

# Comments

Part 21 uses C-style block comments `/* ... */`. Unlike the EXPRESS embedded
remark they do **not** nest — the lexer reads until the first `*/`.

```step21 title="block comments"
/* a single-line comment */
#1= A(1);

/* a comment
   spanning several lines */
#2= B(2);
```

```step21 title="non-nesting comment"
/* outer /* not nested */ #1= A(1);
```

Here the comment closes at the *first* `*/` (the one after `not nested`), so
the rest of the line — `#1= A(1);` — is live exchange content, not comment.

The `/*` and `*/` are recognised only where a token separator may appear, so a
comment can sit between two instances:

```step21 title="comment as a token separator"
#1= A(1) /* comment */ #2= B(2);
```
