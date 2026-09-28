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
            # Section keywords (clause 6.1, 6.2 in the third edition). SIGNATURE
            # is split out below so that its base64 body can be lexed in a state
            # of its own.
            (words(("HEADER", "DATA", "ENDSEC", "ANCHOR", "REFERENCE"),
                   prefix=r"\b", suffix=r"\b"),
             Keyword.Reserved),
            # A signature section opens with the token "SIGNATURE;" (clause
            # 14.1), so the state is entered only when the semicolon follows.
            # Without that lookahead an entity that happens to be named
            # SIGNATURE would swallow the rest of the file as base64.
            (r"\bSIGNATURE\b(?=" + _SEPARATOR + r"*;)", Keyword.Reserved,
             "signature"),
            # Edition 3 resources and anchor names: <uri> and <#fragment>. Both
            # are URIs (clause 6.5), so neither holds whitespace or an angle
            # bracket of its own.
            (r"<[^<>\s]+>", String.Other),
            # Edition 3 occurrence names. A value instance name is "@" DIGIT
            # { DIGIT } and a constant value name is "@" UPPER { UPPER | DIGIT };
            # an occurrence name defines an instance on the left of an
            # assignment and references one on the right, exactly like "#1".
            (r"@\d+(?=" + _SEPARATOR + r"*=)", Name.Label),
            (r"@\d+", Name.Variable),
            (r"@[A-Z][A-Z0-9]*", Name.Constant),
            # Edition 3 constant entity names, "#" UPPER { UPPER | DIGIT }:
            # references like the other occurrence names, never definitions.
            (r"#[A-Z][A-Z0-9]*", Name.Constant),
            (r"#\d+(?=" + _SEPARATOR + r"*=)", Name.Label),            # instance definition
            (r"#\d+", Name.Variable),                    # instance reference
            # >>> Edition 3 anchor tags: {tag_name:'anchor_item'}. The state keeps
            # >>> strings and comments from closing the tag on a "}" inside them.
            (r"\{[A-Za-z_][A-Za-z0-9_]*:", Name.Attribute, "anchor_tag"),
            (r"'", String.Single, "string"),
            # Binary literal (table 2): the first digit is the number of zero
            # bits that were filled in to reach a whole number of octets, so it
            # is 0 to 3, and the empty binary is "0".
            (r'"[0-3][0-9a-f]*"', Number.Hex),
            # Enumeration values: .T., .NOTDEFINED. and values with an
            # underscore such as .LOADING_3D. The WSN subsets of table 1 fold
            # the underscore into UPPER, so it is ordinary grammar anywhere in a
            # value, first position included.
            (r"\.[a-z_][a-z0-9_]*\.", Name.Constant),
            (r"[$*]", Keyword.Constant),                 # unset / derived value
            (r"[+-]?\d+\.\d*(e[+-]?\d+)?", Number.Float),
            (r"[+-]?\d+", Number.Integer),
            (r"!?[a-z_][a-z0-9_]*(?=" + _SEPARATOR + r"*\()",
             Name.Class),                                # entity / typed param
            (r"!?[a-z_][a-z0-9_]*", Name),
            (r"[();,=]", Punctuation),
        ],
        "anchor_tag": [
            # >>> A tag can contain the same separators as the root grammar.
            (_SEPARATOR + "+", Whitespace),
            (r"\\[NF]\\", Comment.Preproc),
            (r"'", String.Single, "string"),
            (r"/\*", Comment.Multiline, "comment"),
            (r"<[^>]*>", String.Other),
            (r"\}", Name.Attribute, "#pop"),
            (r"[^{}'/]+", Name.Attribute),
        ],
        "signature": [
            # >>> Signature bodies are base64 (RFC 4648) and may wrap lines.
            (_SEPARATOR + "+", Whitespace),
            (r"/\*", Comment.Multiline, "comment"),
            (r"\\[NF]\\", Comment.Preproc),
            (r"\bENDSEC\b(?=" + _SEPARATOR + r"*;)", Keyword.Reserved, "root"),
            (r"[A-Za-z0-9+/=]+", String.Other),
            (r";", Punctuation),
        ],
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
        "string": [
            (r"''", String.Escape),
            # A single reverse solidus is written as two (table 2), so the
            # doubled form is one escape rather than two characters.
            (r"\\\\", String.Escape),
            # ISO 10303-21 table 4, string control directives:
            # \S\ \P?\ \X\ \X2\..\X0\ \X4\..\X0\, the last two with one or more
            # groups of four or eight hexadecimal digits.
            (r"\\S\\.|\\P[a-i]\\|\\X\\[0-9a-f]{2}|"
             r"\\X2\\(?:[0-9a-f]{4})+\\X0\\|\\X4\\(?:[0-9a-f]{8})+\\X0\\",
             String.Escape),
            # Table 6 print control directives are allowed within strings too.
            (r"\\[NF]\\", String.Escape),
            (r"'", String.Single, "#pop"),
            (r"[^'\\]+", String.Single),
            (r"\\", String.Single),
        ],
    }
