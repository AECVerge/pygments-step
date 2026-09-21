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
    aliases = ["step21", "p21", "step", "stp", "spf", "iso-10303-21"]
    filenames = ["*.p21", "*.stp", "*.step"]
    mimetypes = ["application/x-step", "model/step"]
    url = "https://en.wikipedia.org/wiki/ISO_10303-21"

    # re.ASCII restricts ``\d``, ``\b`` and the case-insensitive character
    # ranges to ASCII, matching the ISO 10303-21 lexical space (and the EXPRESS
    # lexer above).
    flags = re.IGNORECASE | re.MULTILINE | re.ASCII

    # A token separator is space, a print control directive or a comment (clause
    # 5.6 in both editions). Space is the only whitespace character of the
    # second edition's alphabet, whose 5.2 lets line delimiters through but
    # requires them to be ignored; the third edition widens the alphabet to
    # U+0020 to U+007E plus U+0080 to U+10FFFF and requires the octets outside
    # it - line delimiters "and other control characters such as form feed or
    # character tabulation (tab)" - to be ignored. So the whitespace-like
    # controls separate tokens here; the stranger ones (NUL, ESC, DEL) stay
    # errors, because they do not occur in practice and the error is useful.
    _SEPARATOR = r"[ \t\n\r\f\v]"

    tokens = {
        "root": [
            (_SEPARATOR + "+", Whitespace),
            (r"/\*", Comment.Multiline, "comment"),
            # Print control directives (table 6) may appear at any position
            # where a token separator may appear, not only inside strings
            # (clause 11), so they must be recognised here too.
            (r"\\[NF]\\", Comment.Preproc),
            (r"\b(END-ISO-10303-21|ISO-10303-21)\b", Keyword.Namespace),
            # Section keywords (clause 6.2). HEADER, DATA and ENDSEC are the
            # sections of the second edition; the third edition added the
            # optional ANCHOR, REFERENCE and SIGNATURE sections, whose contents
            # use tokens this lexer does not claim yet.
            (words(("HEADER", "DATA", "ENDSEC", "ANCHOR", "REFERENCE",
                    "SIGNATURE"), prefix=r"\b", suffix=r"\b"),
             Keyword.Reserved),
            (r"#\d+(?=" + _SEPARATOR + r"*=)", Name.Label),            # instance definition
            (r"#\d+", Name.Variable),                    # instance reference
            (r"'", String.Single, "string"),
            (r'"[0-9a-f]*"', Number.Hex),                # binary literal
            # Enumeration values: .T., .NOTDEFINED., but also values that
            # contain an underscore — the grammar allows only letters and
            # digits, while application protocol content such as IFC's
            # .LOADING_3D. needs the underscore — so the rule stays wide.
            (r"\.[a-z_][a-z0-9_]*\.", Name.Constant),
            (r"[$*]", Keyword.Constant),                 # unset / derived value
            (r"[+-]?\d+\.\d*(e[+-]?\d+)?", Number.Float),
            (r"[+-]?\d+", Number.Integer),
            (r"!?[a-z_][a-z0-9_]*(?=" + _SEPARATOR + r"*\()",
             Name.Class),                                # entity / typed param
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
            # ISO 10303-21 table 4, string control directives:
            # \S\ \P?\ \X\ \X2\..\X0\ \X4\..\X0\
            (r"\\S\\.|\\P[a-i]\\|\\X\\[0-9a-f]{2}|"
             r"\\X2\\(?:[0-9a-f]{4})*\\X0\\|\\X4\\(?:[0-9a-f]{8})*\\X0\\",
             String.Escape),
            # Table 6 print control directives are allowed within strings too.
            (r"\\[NF]\\", String.Escape),
            (r"'", String.Single, "#pop"),
            (r"[^'\\]+", String.Single),
            (r"\\", String.Single),
        ],
    }
