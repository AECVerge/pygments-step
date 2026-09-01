"""Pygments lexer for STEP Part 21 exchange files (ISO 10303-21)."""

from __future__ import annotations

import re

from pygments.lexer import RegexLexer, words
from pygments.token import (Comment, Keyword, Name, Number, Punctuation,
                            String, Whitespace)

__all__ = ["StepFileLexer"]


class StepFileLexer(RegexLexer):
    """Lexer for STEP Part 21 exchange files (ISO 10303-21).

    Schema-agnostic: entity names are lexed structurally (any identifier
    followed by ``(``), so the lexer works for IFC, AP203, AP214 and any other
    application protocol without carrying a schema-specific keyword table.

    No application protocol is privileged in the aliases or filename patterns.
    IFC is only one of many SPF-based formats, so ``ifc`` / ``*.ifc`` are
    deliberately not claimed; use ``step21`` (or ``p21`` / ``spf``) for all of
    them.
    """

    name = "STEP Part 21"
    aliases = ["step21", "p21", "step", "stp", "spf"]
    filenames = ["*.p21", "*.stp", "*.step"]
    mimetypes = ["application/x-step", "model/step"]
    url = "https://en.wikipedia.org/wiki/ISO_10303-21"
    version_added = "0.1"

    flags = re.IGNORECASE | re.MULTILINE

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"/\*", Comment.Multiline, "comment"),
            (r"\b(END-ISO-10303-21|ISO-10303-21)\b", Keyword.Namespace),
            (words(("HEADER", "DATA", "ENDSEC", "ANCHOR", "REFERENCE",
                    "SIGNATURE"), prefix=r"\b", suffix=r"\b"),
             Keyword.Reserved),
            (r"#\d+(?=\s*=)", Name.Label),               # instance definition
            (r"#\d+", Name.Variable),                    # instance reference
            (r"'", String.Single, "string"),
            (r'"[0-9a-f]*"', Number.Hex),                # binary literal
            (r"\.[a-z_][a-z0-9_]*\.", Name.Constant),    # .T. .F. .NOTDEFINED.
            (r"[$*]", Keyword.Constant),                 # unset / derived value
            (r"[+-]?\d+\.\d*(e[+-]?\d+)?", Number.Float),
            (r"[+-]?\d+", Number.Integer),
            (r"!?[a-z_][a-z0-9_]*(?=\s*\()", Name.Class),  # entity / typed param
            (r"!?[a-z_][a-z0-9_]*", Name),
            (r"[();,=]", Punctuation),
        ],
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
        "string": [
            (r"''", String.Escape),
            # ISO 10303-21 control directives: \S\ \P?\ \X\ \X2\..\X0\ \X4\..\X0\
            (r"\\S\\.|\\P[a-i]\\|\\X\\[0-9a-f]{2}|"
             r"\\X2\\(?:[0-9a-f]{4})*\\X0\\|\\X4\\(?:[0-9a-f]{8})*\\X0\\",
             String.Escape),
            (r"'", String.Single, "#pop"),
            (r"[^'\\]+", String.Single),
            (r"\\", String.Single),
        ],
    }
